"""
FastAPI application entry point for the Zava AI Agent Platform — Python track.

Startup sequence (lifespan):
  1. Configure OpenTelemetry (→ Application Insights if connection string set)
  2. Instrument FastAPI with OTEL
  3. Load the data store (local or Azure)
  4. Build the inference client (GitHub Models / Azure OpenAI / Foundry)
  5. Build the agent registry (all 5 agents)

The app then serves the shared HTTP API (build-contract §4).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.agents.registry import AgentRegistry
from app.api.routes import router
from app.config import settings
from app.inference.factory import create_chat_client, create_embeddings_client
from app.store.base import ZavaStore
from app.telemetry.otel import configure_telemetry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: setup on entry, teardown on exit."""
    # ── 1. Telemetry ──────────────────────────────────────────────────────
    configure_telemetry(settings.applicationinsights_connection_string or None)

    # ── 2. Data store ─────────────────────────────────────────────────────
    embeddings_client = None
    try:
        embeddings_client = create_embeddings_client(settings)
    except Exception:
        logger.warning(
            "Could not create embeddings client (%s mode); keyword search will be used.",
            settings.embeddings_provider,
        )

    if settings.use_azure_stores:
        from app.store.cosmos import AzureZavaStore

        store: ZavaStore = AzureZavaStore(
            settings,
            embeddings_client=embeddings_client,
            embedding_model=settings.azure_openai_embedding_deployment,
        )
        await store.initialise()
        logger.info("Using AzureZavaStore (Cosmos DB + pgvector)")
    else:
        from app.store.local import LocalZavaStore

        embed_model = (
            settings.github_models_embedding_model
            if settings.embeddings_provider == "github"
            else settings.azure_openai_embedding_deployment
        )
        store = LocalZavaStore(
            data_dir=settings.resolved_data_dir,
            embeddings_client=embeddings_client,
            embedding_model=embed_model,
        )
        await store.initialise()
        logger.info("Using LocalZavaStore (data_dir=%s)", settings.resolved_data_dir)

    app.state.store = store

    # ── 3. Chat inference client ──────────────────────────────────────────
    chat_client = None
    try:
        chat_client = create_chat_client(settings)
        logger.info("Chat client ready (%s)", settings.inference_provider)
    except Exception:
        logger.warning(
            "Could not create chat client (%s mode). "
            "/health and /agents will work; /chat will return 503.",
            settings.inference_provider,
        )

    # ── 4. Agent registry ─────────────────────────────────────────────────
    if chat_client is not None:
        registry = AgentRegistry(chat_client, store, settings)
        registry.build()
    else:
        # Minimal registry that always returns a 503 on chat
        registry = _NoChatRegistry()  # type: ignore[assignment]

    app.state.registry = registry

    logger.info("Zava API ready — provider=%s", settings.inference_provider)
    yield

    # ── Teardown ──────────────────────────────────────────────────────────
    if settings.use_azure_stores and hasattr(store, "close"):
        await store.close()
        logger.info("Azure store connections closed")


# ── Application factory ───────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Zava AI Agent Platform",
        description=(
            "Multi-agent AI platform for Zava intelligent athletic apparel. "
            "Built on Microsoft Agent Framework. "
            "See build-contract.md for the full API specification."
        ),
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(router)

    # Instrument with OpenTelemetry after routes are registered
    FastAPIInstrumentor.instrument_app(app)

    return app


app = create_app()


# ── Fallback registry (no LLM available) ─────────────────────────────────────


class _NoChatRegistry:
    """Minimal registry used when no LLM client can be created at startup."""

    @property
    def metadata(self) -> list[dict[str, str]]:
        from app.agents.registry import AGENT_METADATA

        return AGENT_METADATA

    def get_or_orchestrator(self, key: str | None) -> None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No LLM client available. "
                "Set GITHUB_TOKEN (github mode) or configure Azure credentials."
            ),
        )

    def get(self, key: str) -> None:
        return None
