"""
Agent registry — factory for all Zava agents.

Centralises agent construction so the FastAPI app only needs to interact
with this module.  Agents share a single chat client and data store.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_framework import Agent

from app.agents.concierge import make_concierge_agent
from app.agents.merchandiser import make_merchandiser_agent
from app.agents.operations import make_operations_agent
from app.agents.orchestrator import make_orchestrator_agent
from app.agents.trust import make_trust_agent
from app.store.base import ZavaStore

logger = logging.getLogger(__name__)

# Metadata exposed via GET /agents
AGENT_METADATA = [
    {
        "key": "concierge",
        "name": "Zava Concierge",
        "description": (
            "Customer support: order status, returns, product Q&A, "
            "and knowledge-base search across Zava policies and guides."
        ),
    },
    {
        "key": "merchandiser",
        "name": "Zava Merchandiser",
        "description": (
            "Product insights and recommendations: catalog search, "
            "customer reviews, and sales trend analysis."
        ),
    },
    {
        "key": "operations",
        "name": "Zava Operations",
        "description": (
            "Supply chain and inventory management: stock levels, "
            "supplier document parsing, and restock suggestions."
        ),
    },
    {
        "key": "trust",
        "name": "Zava Trust & Compliance",
        "description": (
            "Content safety screening, policy retrieval, and Module B "
            "audit evidence generation (controls B.1.1–B.4.2)."
        ),
    },
    {
        "key": "orchestrator",
        "name": "Zava Orchestrator",
        "description": (
            "Intelligent router: triages incoming messages and hands off "
            "to the most appropriate specialist agent."
        ),
    },
]


class AgentRegistry:
    """Holds all live agent instances and exposes them by key."""

    def __init__(
        self,
        chat_client: Any,
        store: ZavaStore,
        settings: Any,
    ) -> None:
        self._chat_client = chat_client
        self._store = store
        self._settings = settings
        self._agents: dict[str, Agent] = {}

    def build(self) -> None:
        """Instantiate all agents and the orchestrator."""
        client = self._chat_client
        store = self._store
        s = self._settings

        concierge = make_concierge_agent(client, store)
        merchandiser = make_merchandiser_agent(client, store)
        operations = make_operations_agent(
            client,
            store,
            docintel_endpoint=s.azure_docintel_endpoint,
            azure_client_id=s.azure_client_id,
        )
        trust = make_trust_agent(
            client,
            store,
            contentsafety_endpoint=s.azure_contentsafety_endpoint,
            azure_client_id=s.azure_client_id,
        )
        orchestrator = make_orchestrator_agent(
            client, store, concierge, merchandiser, operations, trust
        )

        self._agents = {
            "concierge": concierge,
            "merchandiser": merchandiser,
            "operations": operations,
            "trust": trust,
            "orchestrator": orchestrator,
        }
        logger.info("Agent registry built: %s", list(self._agents.keys()))

    def get(self, key: str) -> Agent | None:
        """Return an agent by key, or None if not found."""
        return self._agents.get(key)

    def get_or_orchestrator(self, key: str | None) -> Agent:
        """Return the named agent, or the orchestrator if key is None/unknown."""
        if key and key in self._agents:
            return self._agents[key]
        if key and key not in self._agents:
            logger.warning("Unknown agent key %r; using orchestrator", key)
        return self._agents["orchestrator"]

    @property
    def metadata(self) -> list[dict[str, str]]:
        """Return the agent metadata list for GET /agents."""
        return AGENT_METADATA
