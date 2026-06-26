"""
Seed script — loads data/ JSON and Markdown files into Azure stores.

Usage (Azure mode — run after azd provision):
    cd src/python
    python scripts/seed.py

Auth: DefaultAzureCredential (az login or managed identity).
Requires: COSMOS_ENDPOINT, POSTGRES_HOST, AZURE_SEARCH_ENDPOINT set.

What it does:
  1. Upserts products, orders, customers into Cosmos DB (database=zava)
  2. Generates embeddings for policies + supplier docs
  3. Upserts knowledge chunks into PostgreSQL knowledge table (pgvector)
  4. Upserts knowledge chunks into Azure AI Search index
"""

from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import sys
from typing import Any

# Allow running as  python scripts/seed.py  from src/python/
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from app.config import settings
from app.store.postgres import ensure_schema, upsert_knowledge

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = pathlib.Path(settings.resolved_data_dir)


def load_json(filename: str) -> list[dict[str, Any]]:
    path = DATA_DIR / filename
    if not path.exists():
        logger.warning("File not found: %s", path)
        return []
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_markdown_dir(subdir: str) -> list[dict[str, str]]:
    """Load all .md files in data/<subdir>/ as {id, source, title, content}."""
    dir_path = DATA_DIR / subdir
    if not dir_path.exists():
        logger.warning("Directory not found: %s", dir_path)
        return []
    docs = []
    for md_file in sorted(dir_path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        import re

        title_match = re.search(r"^#+\s+(.+)$", content, re.MULTILINE)
        title = (
            title_match.group(1).strip() if title_match else md_file.stem.replace("-", " ").title()
        )
        docs.append(
            {
                "id": f"{subdir}/{md_file.stem}",
                "source": f"{subdir}/{md_file.name}",
                "title": title,
                "content": content,
            }
        )
    return docs


async def seed_cosmos(docs: list[dict[str, Any]], container_name: str) -> None:
    """Upsert items into a Cosmos DB container."""
    from azure.cosmos.aio import CosmosClient
    from azure.identity.aio import DefaultAzureCredential

    if not settings.cosmos_endpoint:
        logger.info("COSMOS_ENDPOINT not set; skipping Cosmos seed for %s", container_name)
        return

    credential = DefaultAzureCredential(managed_identity_client_id=settings.azure_client_id or None)
    async with CosmosClient(settings.cosmos_endpoint, credential) as client:
        db = client.get_database_client(settings.cosmos_database)
        container = db.get_container_client(container_name)
        for doc in docs:
            try:
                await container.upsert_item(doc)
            except Exception:
                logger.exception("Failed to upsert item %s into %s", doc.get("id"), container_name)
    logger.info("Cosmos seed complete for %s (%d items)", container_name, len(docs))


async def embed_documents(
    docs: list[dict[str, str]],
    embed_client: Any,
    model: str,
) -> list[dict[str, Any]]:
    """Generate embeddings for a list of documents in batches of 20."""
    batch_size = 20
    result = []
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        texts = [d["content"][:2000] for d in batch]
        response = await embed_client.embeddings.create(input=texts, model=model)
        for doc, emb_data in zip(batch, response.data, strict=True):
            result.append(
                {
                    "id": doc["id"],
                    "source": doc["source"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "embedding": emb_data.embedding,
                }
            )
        logger.info("Embedded %d/%d documents", min(i + batch_size, len(docs)), len(docs))
    return result


async def seed_postgres(embedded_docs: list[dict[str, Any]]) -> None:
    """Create the knowledge table schema and upsert embedded documents."""
    if not settings.postgres_host:
        logger.info("POSTGRES_HOST not set; skipping PostgreSQL seed")
        return

    import asyncpg
    from azure.identity.aio import DefaultAzureCredential
    from pgvector.asyncpg import register_vector

    credential = DefaultAzureCredential(managed_identity_client_id=settings.azure_client_id or None)
    token = await credential.get_token("https://ossrdbms-aad.database.windows.net/.default")

    pool = await asyncpg.create_pool(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=token.token,
        min_size=1,
        max_size=3,
        init=register_vector,
    )
    try:
        await ensure_schema(pool)
        await upsert_knowledge(pool, embedded_docs)
        logger.info("PostgreSQL seed complete (%d knowledge docs)", len(embedded_docs))
    finally:
        await pool.close()


async def seed_ai_search(embedded_docs: list[dict[str, Any]]) -> None:
    """Index knowledge docs into Azure AI Search."""
    if not settings.azure_search_endpoint:
        logger.info("AZURE_SEARCH_ENDPOINT not set; skipping AI Search seed")
        return

    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents.aio import SearchClient

    credential = DefaultAzureCredential(managed_identity_client_id=settings.azure_client_id or None)
    async with SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=credential,
    ) as client:
        batch = [
            {
                "id": d["id"].replace("/", "_"),
                "source": d["source"],
                "title": d["title"],
                "content": d["content"][:10000],
                # Azure AI Search vector field — configure in index definition
            }
            for d in embedded_docs
        ]
        result = await client.upload_documents(documents=batch)
        logger.info("AI Search upload: %d succeeded", sum(1 for r in result if r.succeeded))


async def main() -> None:
    """Run the full seed pipeline."""
    logger.info("=== Zava Seed Script ===")
    logger.info("Data directory: %s", DATA_DIR)

    if not await asyncio.to_thread(DATA_DIR.exists):
        logger.error("Data directory not found: %s", DATA_DIR)
        sys.exit(1)

    # ── 1. Cosmos DB ──────────────────────────────────────────────────────
    products = load_json("products.json")
    orders = load_json("orders.json")
    customers = load_json("customers.json")

    # Cosmos requires an 'id' field
    for p in products:
        p.setdefault("id", p.get("id", ""))
    for o in orders:
        o.setdefault("id", o.get("orderId", ""))
    for c in customers:
        c.setdefault("id", c.get("id", ""))

    await asyncio.gather(
        seed_cosmos(products, "products"),
        seed_cosmos(orders, "orders"),
        seed_cosmos(customers, "customers"),
    )

    # ── 2. Embeddings + pgvector + AI Search ─────────────────────────────
    from app.inference.factory import create_embeddings_client

    embed_client = None
    embed_model = ""
    try:
        embed_client = create_embeddings_client(settings)
        embed_model = (
            settings.github_models_embedding_model
            if settings.embeddings_provider == "github"
            else settings.azure_openai_embedding_deployment
        )
        logger.info("Embedding client ready (%s)", settings.embeddings_provider)
    except Exception:
        logger.exception("Could not create embeddings client; skipping vector stores")

    if embed_client:
        policies = load_markdown_dir("policies")
        supplier_docs = load_markdown_dir("suppliers")
        all_docs = policies + supplier_docs

        logger.info("Generating embeddings for %d documents...", len(all_docs))
        embedded = await embed_documents(all_docs, embed_client, embed_model)

        await asyncio.gather(
            seed_postgres(embedded),
            seed_ai_search(embedded),
        )
    else:
        logger.warning("Skipping vector stores (no embedding client)")

    logger.info("=== Seed complete ===")


if __name__ == "__main__":
    asyncio.run(main())
