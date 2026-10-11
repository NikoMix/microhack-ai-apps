"""
LocalZavaStore — in-memory data store for GitHub Models / local mode.

Loads all seed data from the data/ directory at startup.  No network or Azure
credentials are required.

Keyword search is used for search_products and search_knowledge when no
embedding client is available.  When an embedding client IS provided, cosine
similarity over in-memory vectors is used for more relevant results.
"""

from __future__ import annotations

import json
import logging
import math
import pathlib
import re
import uuid
from typing import Any

from app.store.base import ZavaStore

logger = logging.getLogger(__name__)


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two float vectors."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _keyword_score(text: str, query: str) -> float:
    """Simple keyword relevance score (fraction of query tokens found in text)."""
    tokens = re.sub(r"[^\w\s]", " ", query.lower()).split()
    if not tokens:
        return 0.0
    text_lower = text.lower()
    return sum(1 for t in tokens if t in text_lower) / len(tokens)


class LocalZavaStore(ZavaStore):
    """In-memory store backed by JSON/Markdown files in data/.

    Parameters
    ----------
    data_dir:
        Absolute path to the repo's data/ directory.
    embeddings_client:
        Optional async OpenAI-compatible client for semantic search.
        If None, keyword search is used.
    embedding_model:
        Model name for the embeddings_client.
    """

    def __init__(
        self,
        data_dir: str,
        embeddings_client: Any | None = None,
        embedding_model: str = "openai/text-embedding-3-small",
    ) -> None:
        self._data_dir = pathlib.Path(data_dir)
        self._embed_client = embeddings_client
        self._embed_model = embedding_model

        # Loaded from JSON files
        self._products: list[dict[str, Any]] = []
        self._reviews: list[dict[str, Any]] = []
        self._orders: list[dict[str, Any]] = []
        self._customers: list[dict[str, Any]] = []

        # Loaded from markdown files
        self._policies: dict[str, dict[str, Any]] = {}  # slug -> {title, content, source}
        self._supplier_docs: dict[str, dict[str, Any]] = {}  # id -> {title, content, source}

        # In-memory vector index: list of {id, text, vector, source, title}
        self._knowledge_index: list[dict[str, Any]] = []
        self._index_built = False

        # Simulated return requests (volatile — not persisted)
        self._returns: list[dict[str, Any]] = []

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def initialise(self) -> None:
        """Load all seed data — implements ZavaStore.initialise()."""
        await self.load()

    async def load(self) -> None:
        """Load all seed data from the data/ directory."""
        self._products = self._load_json("products.json")
        self._reviews = self._load_json("reviews.json")
        self._orders = self._load_json("orders.json")
        self._customers = self._load_json("customers.json")
        self._policies = self._load_markdown_dir("policies")
        self._supplier_docs = self._load_markdown_dir("suppliers")

        # Build the flat knowledge list (no vectors yet — lazy)
        self._knowledge_index = []
        for slug, doc in self._policies.items():
            self._knowledge_index.append({"id": f"policy:{slug}", "text": doc["content"], **doc})
        for doc_id, doc in self._supplier_docs.items():
            self._knowledge_index.append(
                {"id": f"supplier:{doc_id}", "text": doc["content"], **doc}
            )

        logger.info(
            "LocalZavaStore loaded: %d products, %d reviews, %d orders, "
            "%d policies, %d supplier docs",
            len(self._products),
            len(self._reviews),
            len(self._orders),
            len(self._policies),
            len(self._supplier_docs),
        )

    def _load_json(self, filename: str) -> list[dict[str, Any]]:
        path = self._data_dir / filename
        if not path.exists():
            logger.warning("Data file not found: %s", path)
            return []
        with path.open(encoding="utf-8") as f:
            data: list[dict[str, Any]] = json.load(f)
            return data

    def _load_markdown_dir(self, subdir: str) -> dict[str, dict[str, Any]]:
        """Load all .md files in data/<subdir>/ as {slug: {title, content, source}}."""
        result: dict[str, dict[str, Any]] = {}
        dir_path = self._data_dir / subdir
        if not dir_path.exists():
            logger.warning("Data subdirectory not found: %s", dir_path)
            return result
        for md_file in sorted(dir_path.glob("*.md")):
            slug = md_file.stem
            content = md_file.read_text(encoding="utf-8")
            # Extract title from first H1 or H2 heading
            title_match = re.search(r"^#+\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
            result[slug] = {
                "title": title,
                "content": content,
                "source": f"{subdir}/{md_file.name}",
            }
        return result

    # ── Products ─────────────────────────────────────────────────────────

    async def get_product(self, product_id: str) -> dict[str, Any] | None:
        for p in self._products:
            if p.get("id", "").upper() == product_id.upper():
                return p
        return None

    async def search_products(
        self,
        query: str,
        category: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        candidates = self._products
        if category:
            candidates = [
                p
                for p in candidates
                if p.get("category", "").lower() == category.lower()
                or p.get("subcategory", "").lower() == category.lower()
            ]
        scored = []
        for p in candidates:
            text = " ".join(
                [
                    p.get("name", ""),
                    p.get("description", ""),
                    p.get("category", ""),
                    p.get("subcategory", ""),
                    " ".join(p.get("smartFeatures", [])),
                ]
            )
            score = _keyword_score(text, query)
            scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:limit] if _ > 0] or candidates[:limit]

    async def get_all_products(self) -> list[dict[str, Any]]:
        return list(self._products)

    # ── Reviews ──────────────────────────────────────────────────────────

    async def get_reviews(
        self,
        product_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        reviews = self._reviews
        if product_id:
            reviews = [r for r in reviews if r.get("productId", "").upper() == product_id.upper()]
        return reviews[:limit]

    # ── Orders ───────────────────────────────────────────────────────────

    async def get_order(self, order_id: str) -> dict[str, Any] | None:
        for o in self._orders:
            if o.get("orderId", "").upper() == order_id.upper():
                return o
        return None

    async def create_return(
        self,
        order_id: str,
        reason: str,
        items: list[str] | None = None,
    ) -> dict[str, Any]:
        """Simulate creating a return request."""
        return_id = f"ZR-{uuid.uuid4().hex[:6].upper()}"
        record = {
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
        self._returns.append(record)
        return record

    # ── Customers ────────────────────────────────────────────────────────

    async def get_customers(self) -> list[dict[str, Any]]:
        return list(self._customers)

    # ── Knowledge ────────────────────────────────────────────────────────

    async def search_knowledge(
        self,
        query: str,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Search policies and supplier docs.

        Uses cosine similarity when an embedding client is available;
        falls back to keyword scoring.
        """
        if self._embed_client and self._knowledge_index:
            return await self._semantic_search(query, limit)
        return self._keyword_search(query, limit)

    def _keyword_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        scored = []
        for doc in self._knowledge_index:
            score = _keyword_score(doc["text"], query)
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [
            {"source": d["source"], "title": d["title"], "content": d["text"][:800]}
            for _, d in scored[:limit]
            if _ > 0
        ]
        if not results:
            # Return all docs if no keyword match (still show something)
            return [
                {"source": d["source"], "title": d["title"], "content": d["text"][:800]}
                for d in self._knowledge_index[:limit]
            ]
        return results

    async def _semantic_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        """Compute query embedding and find nearest neighbors."""
        if self._embed_client is None:
            return self._keyword_search(query, limit)
        try:
            response = await self._embed_client.embeddings.create(
                input=query,
                model=self._embed_model,
            )
            query_vec: list[float] = response.data[0].embedding

            # Lazily build vectors for knowledge docs on first search
            if not self._index_built:
                await self._build_vectors()

            scored = []
            for doc in self._knowledge_index:
                vec = doc.get("vector")
                if vec:
                    scored.append((_cosine(query_vec, vec), doc))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [
                {"source": d["source"], "title": d["title"], "content": d["text"][:800]}
                for _, d in scored[:limit]
            ]
        except Exception:
            logger.exception("Embedding search failed, falling back to keyword search")
            return self._keyword_search(query, limit)

    async def _build_vectors(self) -> None:
        """Embed all knowledge documents (called once, lazily)."""
        if self._index_built or self._embed_client is None:
            return
        texts = [doc["text"][:2000] for doc in self._knowledge_index]
        if not texts:
            self._index_built = True
            return
        try:
            response = await self._embed_client.embeddings.create(
                input=texts,
                model=self._embed_model,
            )
            for doc, emb in zip(self._knowledge_index, response.data, strict=True):
                doc["vector"] = emb.embedding
            self._index_built = True
            logger.info("Built in-memory vector index (%d docs)", len(texts))
        except Exception:
            logger.exception("Failed to build vector index; keyword search will be used")

    async def get_policy(self, slug: str) -> dict[str, Any] | None:
        """Return a policy by slug (e.g., 'returns', 'warranty')."""
        # Try exact match
        if slug in self._policies:
            p = self._policies[slug]
            return {"source": p["source"], "title": p["title"], "content": p["content"]}
        # Try partial match
        for key, p in self._policies.items():
            if slug.lower() in key.lower() or slug.lower() in p["title"].lower():
                return {"source": p["source"], "title": p["title"], "content": p["content"]}
        return None

    async def get_supplier_doc(self, doc_id: str) -> dict[str, Any] | None:
        """Return a supplier document by ID or partial name."""
        if doc_id in self._supplier_docs:
            d = self._supplier_docs[doc_id]
            return {"source": d["source"], "title": d["title"], "content": d["content"]}
        for key, d in self._supplier_docs.items():
            if doc_id.lower() in key.lower():
                return {"source": d["source"], "title": d["title"], "content": d["content"]}
        return None

    # ── Inventory ─────────────────────────────────────────────────────────

    async def get_inventory(
        self,
        product_id: str | None = None,
    ) -> list[dict[str, Any]]:
        products = self._products
        if product_id:
            products = [p for p in products if p.get("id", "").upper() == product_id.upper()]
        return [
            {
                "productId": p["id"],
                "name": p["name"],
                "inStock": p.get("inStock", 0),
                "category": p.get("category", ""),
            }
            for p in products
        ]
