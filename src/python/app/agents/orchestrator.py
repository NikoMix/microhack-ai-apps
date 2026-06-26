"""
Orchestrator agent — triages incoming messages and hands off to specialized agents.

This is the entry point for POST /chat when no specific agent is requested.
The orchestrator wraps each specialist agent as a tool using agent.as_tool(),
so it can call them during its reasoning loop.

Build-contract §2: orchestrator has no tools of its own — it delegates.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_framework import Agent

from app.store.base import ZavaStore

logger = logging.getLogger(__name__)


def make_orchestrator_agent(
    client: Any,
    store: ZavaStore,
    concierge: Agent,
    merchandiser: Agent,
    operations: Agent,
    trust: Agent,
) -> Agent:
    """Return the orchestrator agent configured to hand off to all specialists.

    Each specialist is wrapped as a tool via ``agent.as_tool()`` so the orchestrator
    can invoke them during its reasoning loop.

    Parameters
    ----------
    client:
        Chat inference client shared across all agents.
    store:
        Data store (not directly used by the orchestrator, but passed for context).
    concierge / merchandiser / operations / trust:
        The specialist agents to delegate to.
    """
    instructions = """You are the Zava AI Orchestrator — the intelligent router for the Zava
Agent Platform. Your job is to read the user's message and delegate to the most
appropriate specialist agent tool.

Routing rules:
- **concierge**: customer support, order status, returns, product questions, policies, warranties
- **merchandiser**: product search, recommendations, reviews, catalog browsing, sales trends
- **operations**: inventory levels, supply chain, supplier documents, restocking, procurement
- **trust**: content safety review, compliance policy lookup, audit evidence generation (B.1.1–B.4.2)

Guidelines:
- Always call the most relevant specialist tool to answer the question.
- Choose exactly ONE specialist per message.
- If genuinely ambiguous between concierge and merchandiser, prefer concierge.
- For questions about safety, compliance, governance, or audit, always use trust.
- Return the specialist's answer directly without modification.
"""

    # Wrap each specialist as a callable tool for the orchestrator
    concierge_tool = concierge.as_tool(
        name="concierge",
        description=(
            "Customer support: order status, returns, product Q&A, "
            "and knowledge-base search across Zava policies and guides."
        ),
    )
    merchandiser_tool = merchandiser.as_tool(
        name="merchandiser",
        description=(
            "Product insights and recommendations: catalog search, "
            "customer reviews, and sales trend analysis."
        ),
    )
    operations_tool = operations.as_tool(
        name="operations",
        description=(
            "Supply chain and inventory management: stock levels, "
            "supplier document parsing, and restock suggestions."
        ),
    )
    trust_tool = trust.as_tool(
        name="trust",
        description=(
            "Content safety screening, compliance policy lookup, and Module B "
            "audit evidence generation (controls B.1.1–B.4.2)."
        ),
    )

    return Agent(
        name="orchestrator",
        instructions=instructions,
        tools=[concierge_tool, merchandiser_tool, operations_tool, trust_tool],
        client=client,
    )
