"""
Merchandiser agent — product insights, recommendations, and review analysis.

Tools (build-contract §2):
  - search_products(query, category)    → relevant product catalog entries
  - get_reviews(product_id)             → customer reviews
  - sales_trends(period)                → aggregated sales / stock trends

Provides buyers, category managers, and the eCommerce team with data-driven
insights on the Zava smart-apparel catalog.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from typing import Any

from agent_framework import Agent, tool

from app.agents.concierge import _add_citation
from app.store.base import ZavaStore

logger = logging.getLogger(__name__)


def make_merchandiser_agent(client: Any, store: ZavaStore) -> Agent:
    """Return a configured Merchandiser agent."""

    @tool
    async def search_products(query: str, category: str = "") -> str:
        """Search the Zava product catalog by keyword or concept.

        Parameters
        ----------
        query:
            Natural-language search string (e.g., "running shirts with heart rate").
        category:
            Optional category filter: Tops, Bottoms, Outerwear, Accessories, Footwear.
        """
        results = await store.search_products(
            query,
            category=category or None,
            limit=5,
        )
        if not results:
            return "No products found matching the query."
        for p in results:
            _add_citation(
                source=f"products/{p.get('id', '')}",
                title=p.get("name", "Product"),
                excerpt=p.get("description", "")[:150],
            )
        return json.dumps(results, default=str, indent=2)

    @tool
    async def get_reviews(product_id: str) -> str:
        """Retrieve customer reviews for a specific Zava product.

        Parameters
        ----------
        product_id:
            Product ID to fetch reviews for (e.g., ZAVA-RUN-001).
            Pass empty string to get all recent reviews.
        """
        reviews = await store.get_reviews(
            product_id=product_id or None,
            limit=10,
        )
        if not reviews:
            return f"No reviews found for product {product_id!r}."
        for r in reviews:
            pid = r.get("productId", "")
            _add_citation(
                source=f"reviews/{pid}",
                title=f"Reviews for {pid}",
                excerpt=r.get("text", "")[:150],
            )
        return json.dumps(reviews, default=str, indent=2)

    @tool
    async def sales_trends(period: str = "all-time") -> str:
        """Return sales and inventory trend summary across the product catalog.

        Parameters
        ----------
        period:
            Reporting period hint (informational — seed data is static).
            Examples: "all-time", "Q2-2026", "this-week".
        """
        products = await store.get_all_products()
        if not products:
            return "No product data available."

        # Aggregate metrics from the seed data
        categories: Counter[str] = Counter()
        total_stock = 0
        low_stock = []
        top_rated = []

        for p in products:
            cat = p.get("category", "Unknown")
            categories[cat] += 1
            stock = p.get("inStock", 0)
            total_stock += stock
            if stock < 100:
                low_stock.append({"id": p["id"], "name": p["name"], "inStock": stock})
            top_rated.append(
                {
                    "id": p["id"],
                    "name": p["name"],
                    "rating": p.get("rating", 0),
                    "price": p.get("price", 0),
                }
            )

        top_rated.sort(key=lambda x: x["rating"], reverse=True)

        summary = {
            "period": period,
            "totalProducts": len(products),
            "totalStock": total_stock,
            "byCategory": dict(categories),
            "lowStockItems": sorted(low_stock, key=lambda x: x["inStock"])[:5],
            "topRatedProducts": top_rated[:5],
        }

        _add_citation(
            source="products/catalog",
            title="Zava Product Catalog",
            excerpt=f"Aggregated sales trends for {period}",
        )
        return json.dumps(summary, indent=2)

    instructions = """You are the Zava Merchandiser — a data-savvy product and category analyst.

Your capabilities:
- Search and compare products across the Zava smart-apparel catalog via search_products
- Retrieve and summarise customer reviews via get_reviews
- Provide sales, inventory, and trend analysis via sales_trends

Guidelines:
- Lead with data: quote ratings, stock levels, and prices when relevant
- Surface smart-feature differentiation (sensors, battery life, app integration)
- Highlight low-stock items and top-rated products proactively
- When asked for recommendations, always match to the customer's stated use case
- Keep insights concise and actionable for buyers and category managers
"""

    return Agent(
        name="merchandiser",
        instructions=instructions,
        tools=[search_products, get_reviews, sales_trends],
        client=client,
    )
