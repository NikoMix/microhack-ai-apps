"""
AzureZavaStore — Cosmos DB + PostgreSQL pgvector + Azure AI Search store.

Used when COSMOS_ENDPOINT is set (Azure mode).
Auth: DefaultAzureCredential everywhere — no keys in code.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.store.base import ZavaStore

logger = logging.getLogger(__name__)


class AzureZavaStore(ZavaStore):
    """Data store backed by Cosmos DB, PostgreSQL pgvector, and Azure AI Search.

    Parameters
    ----------
    settings:
        Application settings singleton.
    embeddings_client:
        Async OpenAI-compatible client for generating query embeddings.
    embedding_model:
        Model name for embeddings (text-embedding-3-small, 1536-dim).
    """

    def __init__(
        self,
        settings: Any,
        embeddings_client: Any,
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        self._settings = settings
        self._embed_client = embeddings_client
        self._embed_model = embedding_model
        self._cosmos_client: Any = None
        self._cosmos_db: Any = None
        self._pg_pool: Any = None

    async def initialise(self) -> None:
        """Open connections to Cosmos DB and PostgreSQL."""
        from azure.cosmos.aio import CosmosClient
        from azure.identity.aio import DefaultAzureCredential

        credential = DefaultAzureCredential(
            managed_identity_client_id=self._settings.azure_client_id or None
        )
        self._cosmos_client = CosmosClient(
            self._settings.cosmos_endpoint,
            credential=credential,
        )
        self._cosmos_db = self._cosmos_client.get_database_client(self._settings.cosmos_database)
        logger.info("Connected to Cosmos DB: %s", self._settings.cosmos_endpoint)

        if self._settings.postgres_host:
            await self._connect_postgres()

    async def _connect_postgres(self) -> None:
        """Connect to PostgreSQL (with pgvector extension)."""
        import asyncpg

        # Use managed identity token for PostgreSQL AAD auth
        from azure.identity.aio import DefaultAzureCredential
        from pgvector.asyncpg import register_vector

        credential = DefaultAzureCredential(
            managed_identity_client_id=self._settings.azure_client_id or None
        )
        token = await credential.get_token("https://ossrdbms-aad.database.windows.net/.default")

        self._pg_pool = await asyncpg.create_pool(
            host=self._settings.postgres_host,
            port=self._settings.postgres_port,
            database=self._settings.postgres_db,
            user=self._settings.postgres_user,
            password=token.token,  # AAD token as password
            min_size=1,
            max_size=5,
            init=register_vector,  # register the vector type adapter
        )
        logger.info("Connected to PostgreSQL: %s", self._settings.postgres_host)

    async def close(self) -> None:
        """Close all connections."""
        if self._cosmos_client:
            await self._cosmos_client.close()
        if self._pg_pool:
            await self._pg_pool.close()

    # ── Helper: Cosmos container ──────────────────────────────────────────

    def _container(self, name: str) -> Any:
        return self._cosmos_db.get_container_client(name)

    # ── Products ─────────────────────────────────────────────────────────

    async def get_product(self, product_id: str) -> dict[str, Any] | None:
        try:
            item = await self._container("products").read_item(
                item=product_id,
                partition_key=product_id,
            )
            return dict(item)
        except Exception:
            return None

    async def search_products(
        self,
        query: str,
        category: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        if self._settings.use_azure_search:
            return await self._search_products_ai_search(query, category, limit)
        # Fallback: Cosmos full-scan
        where = (
            "WHERE CONTAINS(LOWER(c.name), LOWER(@q)) OR CONTAINS(LOWER(c.description), LOWER(@q))"
        )
        params: list[dict[str, Any]] = [{"name": "@q", "value": query}]
        if category:
            where += " AND LOWER(c.category) = LOWER(@cat)"
            params.append({"name": "@cat", "value": category})
        qdef = {
            "query": f"SELECT TOP {limit} * FROM c {where}",  # nosec B608 — limit is int; where uses Cosmos named params
            "parameters": params,
        }
        results = []
        async for item in self._container("products").query_items(
            query=qdef["query"],
            parameters=qdef["parameters"],
        ):
            results.append(dict(item))
        return results

    async def _search_products_ai_search(
        self,
        query: str,
        category: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        from azure.identity.aio import DefaultAzureCredential
        from azure.search.documents.aio import SearchClient

        credential = DefaultAzureCredential(
            managed_identity_client_id=self._settings.azure_client_id or None
        )
        async with SearchClient(
            endpoint=self._settings.azure_search_endpoint,
            index_name=self._settings.azure_search_index,
            credential=credential,
        ) as client:
            filter_expr = f"category eq '{category}'" if category else None
            results = []
            async for result in await client.search(
                search_text=query,
                filter=filter_expr,
                top=limit,
            ):
                results.append(dict(result))
        return results

    async def get_all_products(self) -> list[dict[str, Any]]:
        results = []
        async for item in self._container("products").read_all_items():
            results.append(dict(item))
        return results

    # ── Reviews ──────────────────────────────────────────────────────────

    async def get_reviews(
        self,
        product_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        query = "SELECT TOP @limit * FROM c"
        params: list[dict[str, Any]] = [{"name": "@limit", "value": limit}]
        if product_id:
            query = "SELECT TOP @limit * FROM c WHERE c.productId = @pid"
            params.append({"name": "@pid", "value": product_id})
        results = []
        async for item in self._container("products").query_items(query=query, parameters=params):
            results.append(dict(item))
        return results

    # ── Orders ───────────────────────────────────────────────────────────

    async def get_order(self, order_id: str) -> dict[str, Any] | None:
        try:
            item = await self._container("orders").read_item(item=order_id, partition_key=order_id)
            return dict(item)
        except Exception:
            return None

    async def create_return(
        self,
        order_id: str,
        reason: str,
        items: list[str] | None = None,
    ) -> dict[str, Any]:
        return_id = f"ZR-{uuid.uuid4().hex[:6].upper()}"
        record = {
            "id": return_id,
            "returnId": return_id,
            "orderId": order_id,
            "reason": reason,
            "items": items or [],
            "status": "Pending",
            "message": (
                f"Return {return_id} created for order {order_id}. "
                "Print your prepaid label from the Zava app."
            ),
        }
        await self._container("orders").create_item(body=record)
        return record

    # ── Customers ────────────────────────────────────────────────────────

    async def get_customers(self) -> list[dict[str, Any]]:
        results = []
        async for item in self._container("customers").read_all_items():
            results.append(dict(item))
        return results

    # ── Knowledge (pgvector) ──────────────────────────────────────────────

    async def search_knowledge(
        self,
        query: str,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        if self._pg_pool is None:
            logger.warning("PostgreSQL not connected; returning empty knowledge results")
            return []

        # Generate query embedding
        resp = await self._embed_client.embeddings.create(
            input=query,
            model=self._embed_model,
        )
        query_vec = resp.data[0].embedding

        async with self._pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT source, title, content,
                       1 - (embedding <=> $1::vector) AS similarity
                FROM knowledge
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                query_vec,
                limit,
            )
        return [{"source": r["source"], "title": r["title"], "content": r["content"]} for r in rows]

    async def get_policy(self, slug: str) -> dict[str, Any] | None:
        if self._pg_pool is None:
            return None
        async with self._pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT source, title, content FROM knowledge WHERE source LIKE $1 LIMIT 1",
                f"policies/{slug}%",
            )
        if row:
            return dict(row)
        return None

    async def get_supplier_doc(self, doc_id: str) -> dict[str, Any] | None:
        if self._pg_pool is None:
            return None
        async with self._pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT source, title, content FROM knowledge WHERE source LIKE $1 LIMIT 1",
                f"suppliers/{doc_id}%",
            )
        if row:
            return dict(row)
        return None

    # ── Inventory ─────────────────────────────────────────────────────────

    async def get_inventory(self, product_id: str | None = None) -> list[dict[str, Any]]:
        if product_id:
            item = await self.get_product(product_id)
            if item:
                return [
                    {
                        "productId": item["id"],
                        "name": item["name"],
                        "inStock": item.get("inStock", 0),
                        "category": item.get("category", ""),
                    }
                ]
            return []
        products = await self.get_all_products()
        return [
            {
                "productId": p["id"],
                "name": p["name"],
                "inStock": p.get("inStock", 0),
                "category": p.get("category", ""),
            }
            for p in products
        ]
