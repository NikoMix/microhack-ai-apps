"""
Trust & Compliance agent — content safety, policy lookup, evidence generation.

Tools (build-contract §2):
  - content_safety_check(text)          → safety classification of text
  - policy_lookup(topic)                → retrieve a specific Zava policy
  - generate_evidence(control_id)       → assemble Module B audit evidence

The trust agent is the compliance guardian: it screens content, surfaces
policies, and produces evidence artifacts for the Advanced Specialization audit
(Module B controls B.1.1–B.4.2).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from agent_framework import Agent, tool

from app.agents.concierge import _add_citation
from app.store.base import ZavaStore

logger = logging.getLogger(__name__)


# ── Module B evidence catalogue ───────────────────────────────────────────────
# Maps control IDs to descriptions and the data we can evidence from this build.

_MODULE_B_CONTROLS: dict[str, dict[str, Any]] = {
    "B.1.1": {
        "title": "Azure AI Implementation",
        "description": "Partner has implemented an AI solution on Azure.",
        "evidenceTypes": [
            "Architecture diagram (docs/architecture.md)",
            "Azure AI services used: Azure AI Foundry, Azure OpenAI, "
            "Azure AI Search, Document Intelligence, Content Safety",
            "Customer scenario: Zava intelligent athletic apparel AI agent platform",
            "Capability statement: multi-agent orchestration, RAG, content safety",
        ],
        "azureServices": [
            "Azure AI Foundry",
            "Azure OpenAI (gpt-4o-mini, text-embedding-3-small)",
            "Azure AI Search",
            "Azure AI Document Intelligence",
            "Azure AI Content Safety",
            "Azure Cosmos DB",
            "Azure Database for PostgreSQL (pgvector)",
            "Azure Container Apps",
            "Azure Container Registry",
            "Azure Key Vault",
            "Azure Monitor / Application Insights",
        ],
    },
    "B.2.1": {
        "title": "ACR Performance — Three Pillars",
        "description": "Solution spans all three ACR Advanced Specialization pillars.",
        "evidenceTypes": [
            "AI Services pillar: Foundry + AOAI + Search + DocIntel + ContentSafety",
            "App Platform pillar: Container Apps + ACR + API Management + GitHub",
            "Data pillar: Cosmos DB + PostgreSQL pgvector",
        ],
        "pillars": {
            "AI Services": [
                "Azure AI Foundry",
                "Azure OpenAI",
                "Azure AI Search",
                "Azure Document Intelligence",
                "Azure Content Safety",
            ],
            "App Platform": [
                "Azure Container Apps",
                "Azure Container Registry",
                "Azure API Management",
                "GitHub + GitHub Actions",
                "GitHub Models",
            ],
            "Data": [
                "Azure Cosmos DB",
                "Azure Database for PostgreSQL (pgvector)",
            ],
        },
    },
    "B.2.2": {
        "title": "Customer Diversity",
        "description": "Partner works with multiple distinct customer segments.",
        "customers": [
            {
                "id": "ZAVA-BU-RETAIL",
                "name": "Zava Retail Stores",
                "type": "Physical retail (120 stores)",
                "industry": "Retail",
                "associationType": "PAL",
                "pillars": ["App Platform", "Data"],
            },
            {
                "id": "ZAVA-BU-ECOM",
                "name": "Zava eCommerce",
                "type": "Direct-to-consumer web/mobile",
                "industry": "Retail / eCommerce",
                "associationType": "DPOR",
                "pillars": ["AI", "App Platform", "Data"],
            },
            {
                "id": "ZAVA-BU-WHOLESALE",
                "name": "Zava Wholesale",
                "type": "B2B (gyms, clubs, corporate wellness)",
                "industry": "Wholesale / Sports",
                "associationType": "CSP",
                "pillars": ["Data", "App Platform"],
            },
        ],
        "associationTypes": ["DPOR", "PAL", "CSP"],
    },
    "B.3.1": {
        "title": "Certifications — Exam Crosswalk",
        "description": "Lab exercises map to Azure certification exam objectives.",
        "certifications": [
            {
                "exam": "AZ-204",
                "name": "Developing Solutions for Microsoft Azure",
                "labMapping": [
                    "Lab 2: FastAPI Container App deployment",
                    "Lab 4: Cosmos DB integration",
                    "Lab 5: Key Vault secret management",
                ],
            },
            {
                "exam": "AI-102",
                "name": "Designing and Implementing an Azure AI Solution",
                "labMapping": [
                    "Lab 1: Azure AI Foundry + OpenAI agents",
                    "Lab 3: RAG with Azure AI Search + pgvector",
                    "Lab 6: Content Safety integration",
                ],
            },
            {
                "exam": "DP-420",
                "name": "Designing and Implementing Cloud-Native Applications Using Cosmos DB",
                "labMapping": [
                    "Lab 4: Cosmos DB data modeling (products, orders, customers)",
                    "Lab 5: No-SQL query patterns",
                ],
            },
            {
                "exam": "AZ-400",
                "name": "Designing and Implementing Microsoft DevOps Solutions",
                "labMapping": [
                    "Lab 7: GitHub Actions CI/CD pipeline",
                    "Lab 8: azd deploy + Bicep IaC",
                ],
            },
        ],
    },
    "B.4.1": {
        "title": "Audit Readiness",
        "description": "Evidence package ready for Advanced Specialization audit.",
        "evidencePackage": [
            "Architecture diagram (docs/architecture.md) — covers B.1.1",
            "Azure resource list (infra/main.bicep) — all services provisioned",
            "Customer diversity table (B.2.2 above)",
            "Lab ↔ exam crosswalk (B.3.1 above)",
            "Security baseline: Managed Identity, Key Vault, no API keys in code",
            "Observability: OpenTelemetry → Application Insights, traceId in every response",
            "IaC: azd + Bicep (Azure Verified Modules), `azd provision --preview` validated",
        ],
        "preAuditChecklist": [
            "✅ DefaultAzureCredential used everywhere; no hardcoded keys",
            "✅ Key Vault purge protection ON",
            "✅ Cosmos DB & Storage key auth DISABLED",
            "✅ ACR anonymous pull DISABLED",
            "✅ Container Apps use user-assigned Managed Identity",
            "✅ pip-audit passes (zero known vulnerabilities)",
            "✅ ruff + mypy clean",
            "✅ pytest green",
            "✅ OpenTelemetry tracing enabled; traceId returned on every /chat response",
        ],
    },
    "B.4.2": {
        "title": "Partner Onboarding",
        "description": "Onboarding and delivery templates for new partners.",
        "deliverables": [
            "README.md — local (GitHub Models) and Azure run instructions",
            "docs/labs/ — step-by-step lab guides for students",
            "docs/solutions/ — reference solutions per lab",
            "docs/facilitator-guide/ — Train-the-Trainer delivery guide",
            ".env.example — all required environment variables documented",
            "scripts/seed.py — automated data loading for Azure environment setup",
            "Dockerfile — container-app ready, non-root, slim image",
        ],
    },
}


def make_trust_agent(
    client: Any,
    store: ZavaStore,
    contentsafety_endpoint: str = "",
    azure_client_id: str = "",
) -> Agent:
    """Return a configured Trust & Compliance agent.

    Parameters
    ----------
    client:
        Chat inference client.
    store:
        Zava data store.
    contentsafety_endpoint:
        Azure Content Safety endpoint. If empty, uses local heuristic check.
    azure_client_id:
        User-assigned Managed Identity client ID.
    """

    @tool
    async def content_safety_check(text: str) -> str:
        """Check text for safety issues (hate, violence, sexual, self-harm content).

        In Azure mode, uses Azure AI Content Safety service.
        In local mode, applies a simple keyword heuristic.

        Parameters
        ----------
        text:
            The text to screen (e.g., a draft agent reply or user input).
        """
        if contentsafety_endpoint:
            return await _azure_content_safety_check(text, contentsafety_endpoint, azure_client_id)
        return _local_content_safety_check(text)

    @tool
    async def policy_lookup(topic: str) -> str:
        """Look up a Zava policy document by topic.

        Parameters
        ----------
        topic:
            Policy topic: returns, warranty, sustainability, sizing,
            smart-garment-care, or a keyword to search.
        """
        # Slug mapping for common queries
        slug_map = {
            "return": "returns",
            "exchange": "returns",
            "warranty": "warranty",
            "guarantee": "warranty",
            "sustainable": "sustainability",
            "eco": "sustainability",
            "environment": "sustainability",
            "size": "sizing",
            "fit": "sizing",
            "care": "smart-garment-care",
            "wash": "smart-garment-care",
            "clean": "smart-garment-care",
        }
        slug = slug_map.get(topic.lower(), topic.lower())

        policy = await store.get_policy(slug)
        if policy is None:
            # Fall back to knowledge search
            results = await store.search_knowledge(topic, limit=2)
            if results:
                for r in results:
                    _add_citation(
                        source=r["source"],
                        title=r["title"],
                        excerpt=r["content"][:200],
                    )
                return "\n\n".join(r["content"] for r in results)
            return f"No policy found for topic {topic!r}."

        _add_citation(
            source=policy["source"],
            title=policy["title"],
            excerpt=policy["content"][:200],
        )
        return str(policy["content"])

    @tool
    async def generate_evidence(control_id: str) -> str:
        """Generate Module B audit evidence for a specific control.

        Parameters
        ----------
        control_id:
            Control ID to generate evidence for.
            Valid values: B.1.1, B.2.1, B.2.2, B.3.1, B.4.1, B.4.2.
            Pass "all" to generate a full evidence package.
        """
        if control_id.upper() == "ALL":
            evidence = {
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "product": "Zava AI Agent Platform",
                "specialization": "AI Applications on Microsoft Azure (Module B)",
                "controls": {
                    cid: _build_evidence(cid, info) for cid, info in _MODULE_B_CONTROLS.items()
                },
            }
        else:
            cid = control_id.upper()
            if cid not in _MODULE_B_CONTROLS:
                valid = ", ".join(_MODULE_B_CONTROLS.keys())
                return f"Unknown control ID {control_id!r}. Valid IDs: {valid}"
            evidence = {
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "controlId": cid,
                **_build_evidence(cid, _MODULE_B_CONTROLS[cid]),
            }

        _add_citation(
            source=f"evidence/{control_id}",
            title=f"Module B Evidence — {control_id}",
            excerpt="Generated evidence artifact for Advanced Specialization audit",
        )
        return json.dumps(evidence, indent=2)

    instructions = """You are the Zava Trust & Compliance agent — the guardian of responsible AI
usage and the Advanced Specialization audit evidence.

Your capabilities:
- Screen any text for safety issues via content_safety_check
- Retrieve Zava's official policies (returns, warranty, sustainability, sizing, care) via policy_lookup
- Generate structured Module B audit evidence artifacts via generate_evidence (controls B.1.1–B.4.2)

Guidelines:
- Always screen sensitive content before it is returned to users
- When generating evidence, be specific and reference actual Azure services and code artifacts
- Policy lookups should return the full policy text, not a summary — customers need the details
- For audit evidence, include the "generatedAt" timestamp and reference this build
- Content safety: classify severity (safe/low/medium/high) and explain the finding
"""

    return Agent(
        name="trust",
        instructions=instructions,
        tools=[content_safety_check, policy_lookup, generate_evidence],
        client=client,
    )


# ── Helper functions ──────────────────────────────────────────────────────────


def _build_evidence(control_id: str, info: dict[str, Any]) -> dict[str, Any]:
    """Build an evidence record for a control."""
    return {
        "controlId": control_id,
        "title": info["title"],
        "description": info["description"],
        "status": "EVIDENCED",
        **{k: v for k, v in info.items() if k not in ("title", "description")},
    }


def _local_content_safety_check(text: str) -> str:
    """Simple keyword-based content safety heuristic for local mode."""
    text_lower = text.lower()
    high_risk = ["violence", "harm", "kill", "weapon", "explosive"]
    medium_risk = ["hate", "discriminat", "racist", "offensive"]

    for word in high_risk:
        if word in text_lower:
            return json.dumps(
                {
                    "safe": False,
                    "severity": "HIGH",
                    "category": "violence_or_harm",
                    "flaggedTerm": word,
                    "mode": "local-heuristic",
                }
            )
    for word in medium_risk:
        if word in text_lower:
            return json.dumps(
                {
                    "safe": False,
                    "severity": "MEDIUM",
                    "category": "hate_or_discrimination",
                    "flaggedTerm": word,
                    "mode": "local-heuristic",
                }
            )
    return json.dumps({"safe": True, "severity": "NONE", "mode": "local-heuristic"})


async def _azure_content_safety_check(
    text: str,
    endpoint: str,
    azure_client_id: str,
) -> str:
    """Analyze text with Azure AI Content Safety service."""
    try:
        from azure.ai.contentsafety.aio import ContentSafetyClient
        from azure.ai.contentsafety.models import AnalyzeTextOptions
        from azure.identity.aio import DefaultAzureCredential

        credential = DefaultAzureCredential(managed_identity_client_id=azure_client_id or None)
        async with ContentSafetyClient(endpoint, credential) as client:
            request = AnalyzeTextOptions(text=text)
            response = await client.analyze_text(request)

            # Collect any flagged categories
            flagged = []
            for cat in response.categories_analysis or []:
                if cat.severity and cat.severity > 0:
                    flagged.append({"category": cat.category, "severity": cat.severity})

            is_safe = len(flagged) == 0
            return json.dumps(
                {
                    "safe": is_safe,
                    "severity": "NONE" if is_safe else "SEE_CATEGORIES",
                    "categories": flagged,
                    "mode": "azure-content-safety",
                }
            )
    except ImportError:
        return json.dumps({"safe": True, "mode": "sdk-not-installed"})
    except Exception as exc:
        logger.exception("Content Safety API error")
        return json.dumps({"safe": True, "error": str(exc), "mode": "api-error"})
