"""
Concierge agent — customer support, order status, returns, product Q&A.

Tools (build-contract §2):
  - get_order(order_id)                 → order details
  - get_product(product_id)             → product details
  - search_knowledge(query)             → policy / doc RAG search
  - create_return(order_id, reason)     → initiate a return

The concierge grounds every response in real Zava data and policies,
citing sources so the RAG chain is transparent.
"""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from typing import Any

from agent_framework import Agent, tool

from app.store.base import ZavaStore

logger = logging.getLogger(__name__)

# Thread-local citation accumulator (reset per request in routes.py)
# Using None as default to avoid mutable default (B039); reset_citations initializes it.
_citations: ContextVar[list[dict[str, Any]] | None] = ContextVar("citations", default=None)


def get_citations() -> list[dict[str, Any]]:
    """Return citations accumulated during the current agent run."""
    return list(_citations.get() or [])


def reset_citations() -> None:
    """Clear the citation list for a new request."""
    _citations.set([])


def _add_citation(source: str, title: str, excerpt: str = "") -> None:
    current = _citations.get()
    if current is None:
        current = []
        _citations.set(current)
    # Avoid duplicates
    for c in current:
        if c["source"] == source:
            return
    current.append({"source": source, "title": title, "excerpt": excerpt[:200]})


def make_concierge_agent(client: Any, store: ZavaStore) -> Agent:
    """Return a configured Concierge agent with its tool set.

    The agent is stateless — session history is managed externally by the
    orchestrator (passed as message context).
    """

    @tool
    async def get_order(order_id: str) -> str:
        """Look up a Zava order by its order ID (e.g., ZO-100431).

        Returns the order status, items, total, and shipping information.
        """
        order = await store.get_order(order_id)
        if order is None:
            return f"Order {order_id!r} was not found. Please verify the order ID."
        _add_citation(
            source=f"orders/{order_id}",
            title=f"Order {order_id}",
            excerpt=f"Status: {order.get('status')}, Total: {order.get('total')}",
        )
        return json.dumps(order, default=str, indent=2)

    @tool
    async def get_product(product_id: str) -> str:
        """Look up a Zava product by its product ID (e.g., ZAVA-RUN-001).

        Returns name, category, price, smart features, and stock level.
        """
        product = await store.get_product(product_id)
        if product is None:
            return f"Product {product_id!r} was not found."
        _add_citation(
            source=f"products/{product_id}",
            title=product.get("name", product_id),
            excerpt=product.get("description", "")[:200],
        )
        return json.dumps(product, default=str, indent=2)

    @tool
    async def search_knowledge(query: str) -> str:
        """Search Zava's knowledge base (policies, product docs, supplier guides).

        Use this to answer questions about returns, warranty, sizing, sustainability,
        smart-garment care, and general product information.

        Parameters
        ----------
        query:
            Natural-language search query.
        """
        results = await store.search_knowledge(query, limit=3)
        if not results:
            return "No relevant information found in the Zava knowledge base."
        output_parts = []
        for r in results:
            _add_citation(
                source=r["source"],
                title=r["title"],
                excerpt=r["content"][:200],
            )
            output_parts.append(f"## {r['title']}\nSource: {r['source']}\n\n{r['content']}")
        return "\n\n---\n\n".join(output_parts)

    @tool
    async def create_return(order_id: str, reason: str) -> str:
        """Initiate a return for a Zava order.

        Parameters
        ----------
        order_id:
            The Zava order ID to return (e.g., ZO-100435).
        reason:
            Customer's reason for the return (e.g., "wrong size", "defective").
        """
        # Verify the order exists first
        order = await store.get_order(order_id)
        if order is None:
            return f"Cannot create return: order {order_id!r} not found."

        result = await store.create_return(order_id, reason)
        _add_citation(
            source=f"returns/{result['returnId']}",
            title=f"Return {result['returnId']}",
            excerpt=result.get("message", ""),
        )
        return json.dumps(result, default=str, indent=2)

    instructions = """You are the Zava Concierge — a friendly, knowledgeable customer support
agent for Zava's intelligent athletic apparel.

Your capabilities:
- Look up order status and tracking via get_order
- Find product details and availability via get_product
- Answer questions about policies (returns, warranty, sizing, sustainability, care) via search_knowledge
- Create return requests via create_return

Guidelines:
- Always verify order or product IDs before providing details
- Cite the source of policy information so customers know where it comes from
- For return requests, check the returns policy first to set expectations
- Be empathetic and concise; this is often a time-sensitive interaction
- If you cannot find the requested information, say so clearly and suggest alternatives
- Smart-garment specifics: remind customers to factory-reset before returning electronics
"""

    return Agent(
        name="concierge",
        instructions=instructions,
        tools=[get_order, get_product, search_knowledge, create_return],
        client=client,
    )
