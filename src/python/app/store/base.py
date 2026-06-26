"""
Abstract base class for the Zava data store.

Concrete implementations:
  - LocalZavaStore   (in-memory, loaded from data/ JSON/markdown files)
  - AzureZavaStore   (Cosmos DB + PostgreSQL pgvector + AI Search)

All methods are async to keep the interface consistent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ZavaStore(ABC):
    """Data access interface for Zava seed data and knowledge."""

    # ── Products ─────────────────────────────────────────────────────────

    @abstractmethod
    async def get_product(self, product_id: str) -> dict[str, Any] | None:
        """Return a single product by ID, or None if not found."""

    @abstractmethod
    async def search_products(
        self,
        query: str,
        category: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Full-text / semantic search on the product catalog."""

    @abstractmethod
    async def get_all_products(self) -> list[dict[str, Any]]:
        """Return all products (for sales_trends aggregation)."""

    # ── Reviews ──────────────────────────────────────────────────────────

    @abstractmethod
    async def get_reviews(
        self,
        product_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return reviews, optionally filtered by product ID."""

    # ── Orders ───────────────────────────────────────────────────────────

    @abstractmethod
    async def get_order(self, order_id: str) -> dict[str, Any] | None:
        """Return a single order by order ID, or None."""

    @abstractmethod
    async def create_return(
        self,
        order_id: str,
        reason: str,
        items: list[str] | None = None,
    ) -> dict[str, Any]:
        """Record a return request for an order."""

    # ── Customers ────────────────────────────────────────────────────────

    @abstractmethod
    async def get_customers(self) -> list[dict[str, Any]]:
        """Return all Zava business-unit customers."""

    # ── Knowledge (policies + supplier docs) ─────────────────────────────

    @abstractmethod
    async def search_knowledge(
        self,
        query: str,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Semantic / keyword search over policies and supplier docs.

        Returns a list of dicts with keys: source, title, content.
        """

    @abstractmethod
    async def get_policy(self, slug: str) -> dict[str, Any] | None:
        """Return the full text of a specific policy by slug.

        Known slugs: returns, warranty, sustainability, sizing, smart-garment-care.
        """

    @abstractmethod
    async def get_supplier_doc(self, doc_id: str) -> dict[str, Any] | None:
        """Return parsed content of a supplier document by ID."""

    # ── Inventory helpers ─────────────────────────────────────────────────

    @abstractmethod
    async def get_inventory(
        self,
        product_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return inventory levels. If product_id is None, return all."""

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def initialise(self) -> None:
        """Load or connect the store — called once at app startup.

        Default is a no-op; subclasses override to load files or open connections.
        """
        # Concrete default: nothing to do. Subclasses override.
        return  # noqa: PLR0206
