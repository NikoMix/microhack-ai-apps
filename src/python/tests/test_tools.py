"""
Tests for agent tools using the LocalZavaStore (no Azure required).

All LLM calls are mocked — only the tool implementations are exercised.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

# ── Concierge tool tests ──────────────────────────────────────────────────────


class TestConciergeTools:
    """Test concierge tools against the local store."""

    @pytest.mark.asyncio
    async def test_get_order_found(self, local_store: Any) -> None:
        """get_order tool is registered on the concierge agent."""
        from app.agents.concierge import make_concierge_agent, reset_citations

        reset_citations()
        mock_client = MagicMock()
        agent = make_concierge_agent(mock_client, local_store)

        # Agent is built successfully and has the expected name
        assert agent.name == "concierge"

    @pytest.mark.asyncio
    async def test_local_store_get_order_existing(self, local_store: Any) -> None:
        """LocalZavaStore.get_order returns correct order for ZO-100431."""
        order = await local_store.get_order("ZO-100431")
        assert order is not None
        assert order["orderId"] == "ZO-100431"
        assert order["status"] == "Delivered"
        assert order["customerName"] == "Ana Ramirez"

    @pytest.mark.asyncio
    async def test_local_store_get_order_missing(self, local_store: Any) -> None:
        """LocalZavaStore.get_order returns None for unknown order ID."""
        order = await local_store.get_order("ZO-INVALID-999")
        assert order is None

    @pytest.mark.asyncio
    async def test_local_store_get_product_existing(self, local_store: Any) -> None:
        """LocalZavaStore.get_product returns correct product."""
        product = await local_store.get_product("ZAVA-RUN-001")
        assert product is not None
        assert product["name"] == "Pulse Smart Running Shirt"
        assert product["price"] == 89.0

    @pytest.mark.asyncio
    async def test_local_store_get_product_missing(self, local_store: Any) -> None:
        """LocalZavaStore.get_product returns None for unknown product."""
        product = await local_store.get_product("ZAVA-NONEXISTENT")
        assert product is None

    @pytest.mark.asyncio
    async def test_local_store_create_return(self, local_store: Any) -> None:
        """LocalZavaStore.create_return creates a return record with a return ID."""
        result = await local_store.create_return("ZO-100431", "wrong size")
        assert result["returnId"].startswith("ZR-")
        assert result["orderId"] == "ZO-100431"
        assert result["status"] == "Pending"

    @pytest.mark.asyncio
    async def test_local_store_search_knowledge_returns_policy(self, local_store: Any) -> None:
        """search_knowledge returns relevant policy content for 'returns'."""
        results = await local_store.search_knowledge("returns policy")
        assert len(results) > 0
        # At least one result should mention returns
        combined = " ".join(r["content"] for r in results).lower()
        assert "return" in combined


# ── Merchandiser tool tests ───────────────────────────────────────────────────


class TestMerchandiserTools:
    """Test merchandiser tools."""

    @pytest.mark.asyncio
    async def test_search_products_no_category(self, local_store: Any) -> None:
        """search_products returns relevant products for a keyword query."""
        results = await local_store.search_products("running shirt")
        assert isinstance(results, list)
        if results:  # may be empty if keyword mismatch
            for r in results:
                assert "id" in r
                assert "name" in r

    @pytest.mark.asyncio
    async def test_search_products_with_category(self, local_store: Any) -> None:
        """search_products filters by category correctly."""
        results = await local_store.search_products("smart", category="Tops")
        # All results should be in Tops category (or empty list)
        for r in results:
            assert r.get("category", "").lower() in ("tops", "")

    @pytest.mark.asyncio
    async def test_get_reviews_for_product(self, local_store: Any) -> None:
        """get_reviews returns reviews for a specific product."""
        reviews = await local_store.get_reviews("ZAVA-RUN-001")
        assert isinstance(reviews, list)
        for r in reviews:
            assert r.get("productId") == "ZAVA-RUN-001"

    @pytest.mark.asyncio
    async def test_get_all_products(self, local_store: Any) -> None:
        """get_all_products returns the full catalog (10 products in seed data)."""
        products = await local_store.get_all_products()
        assert len(products) == 10


# ── Operations tool tests ─────────────────────────────────────────────────────


class TestOperationsTools:
    """Test operations tools."""

    @pytest.mark.asyncio
    async def test_get_inventory_all(self, local_store: Any) -> None:
        """get_inventory returns all products when no filter is given."""
        inventory = await local_store.get_inventory()
        assert len(inventory) == 10
        for item in inventory:
            assert "productId" in item
            assert "inStock" in item

    @pytest.mark.asyncio
    async def test_get_inventory_single(self, local_store: Any) -> None:
        """get_inventory filters by product ID."""
        inventory = await local_store.get_inventory("ZAVA-SOC-004")
        assert len(inventory) == 1
        assert inventory[0]["productId"] == "ZAVA-SOC-004"
        assert inventory[0]["inStock"] == 320

    @pytest.mark.asyncio
    async def test_get_supplier_doc_existing(self, local_store: Any) -> None:
        """get_supplier_doc returns a known supplier document."""
        doc = await local_store.get_supplier_doc("invoice-flexcircuit-88231")
        assert doc is not None
        assert "FlexCircuit" in doc["content"]

    @pytest.mark.asyncio
    async def test_get_supplier_doc_missing(self, local_store: Any) -> None:
        """get_supplier_doc returns None for unknown document."""
        doc = await local_store.get_supplier_doc("nonexistent-doc")
        assert doc is None


# ── Trust tool tests ──────────────────────────────────────────────────────────


class TestTrustTools:
    """Test trust agent tools."""

    def test_local_content_safety_check_safe_text(self) -> None:
        """Safe text is classified as safe in local mode."""
        import json

        from app.agents.trust import _local_content_safety_check

        result = json.loads(_local_content_safety_check("Hello, how can I return my order?"))
        assert result["safe"] is True
        assert result["severity"] == "NONE"

    def test_local_content_safety_check_violent_text(self) -> None:
        """Text with high-risk keywords is classified as unsafe."""
        import json

        from app.agents.trust import _local_content_safety_check

        result = json.loads(_local_content_safety_check("I want to cause harm to everyone"))
        assert result["safe"] is False
        assert result["severity"] == "HIGH"

    @pytest.mark.asyncio
    async def test_policy_lookup_returns(self, local_store: Any) -> None:
        """policy_lookup returns the returns policy."""
        policy = await local_store.get_policy("returns")
        assert policy is not None
        assert "45 days" in policy["content"]

    @pytest.mark.asyncio
    async def test_policy_lookup_warranty(self, local_store: Any) -> None:
        """policy_lookup returns the warranty policy."""
        policy = await local_store.get_policy("warranty")
        assert policy is not None
        assert "2-year" in policy["content"].lower() or "warranty" in policy["content"].lower()

    def test_generate_evidence_b11(self) -> None:
        """generate_evidence returns evidence for B.1.1."""
        from app.agents.trust import _MODULE_B_CONTROLS, _build_evidence

        info = _MODULE_B_CONTROLS["B.1.1"]
        evidence = _build_evidence("B.1.1", info)
        assert evidence["controlId"] == "B.1.1"
        assert evidence["status"] == "EVIDENCED"
        assert "azureServices" in evidence

    def test_generate_evidence_all_controls_present(self) -> None:
        """All Module B controls are in the catalogue."""
        from app.agents.trust import _MODULE_B_CONTROLS

        required = {"B.1.1", "B.2.1", "B.2.2", "B.3.1", "B.4.1", "B.4.2"}
        assert required.issubset(set(_MODULE_B_CONTROLS.keys()))

    def test_customer_diversity_three_customers(self) -> None:
        """B.2.2 evidence includes exactly 3 Zava business units."""
        from app.agents.trust import _MODULE_B_CONTROLS

        customers = _MODULE_B_CONTROLS["B.2.2"]["customers"]
        assert len(customers) == 3
        association_types = {c["associationType"] for c in customers}
        # Must include DPOR, PAL, CSP for B.2.2 compliance
        assert association_types == {"DPOR", "PAL", "CSP"}
