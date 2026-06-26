"""
Pytest fixtures shared across all test modules.

LLM calls are always mocked so tests run offline with no credentials.
"""

from __future__ import annotations

import pathlib
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# ── Path to the repo's data/ directory ───────────────────────────────────────

DATA_DIR = str(pathlib.Path(__file__).parent.parent.parent.parent / "data")


# ── App fixture with mocked LLM ───────────────────────────────────────────────


@pytest.fixture(scope="session")
def mock_chat_client() -> MagicMock:
    """A mock agent-framework chat client."""
    client = MagicMock()
    return client


@pytest.fixture(scope="session")
def mock_embeddings_client() -> AsyncMock:
    """A mock OpenAI-compatible embeddings client."""
    embed_client = AsyncMock()
    embed_data = MagicMock()
    embed_data.embedding = [0.01] * 1536  # 1536-dim zero-ish vector
    response = MagicMock()
    response.data = [embed_data]
    embed_client.embeddings.create = AsyncMock(return_value=response)
    return embed_client


@pytest.fixture(scope="session")
def local_store(mock_embeddings_client: AsyncMock) -> Any:
    """A LocalZavaStore loaded with real seed data."""
    import asyncio

    from app.store.local import LocalZavaStore

    store = LocalZavaStore(
        data_dir=DATA_DIR,
        embeddings_client=mock_embeddings_client,
        embedding_model="openai/text-embedding-3-small",
    )
    asyncio.run(store.load())
    return store


@pytest.fixture(scope="session")
def app(local_store: Any, mock_chat_client: MagicMock) -> Any:
    """Create a FastAPI test app with mocked LLM and local store."""
    from app.agents.registry import AgentRegistry
    from app.config import settings
    from app.main import create_app

    test_app = create_app()

    # Patch the lifespan to use our fixtures instead of real providers

    registry = AgentRegistry(mock_chat_client, local_store, settings)
    registry.build()

    test_app.state.store = local_store
    test_app.state.registry = registry
    return test_app


@pytest.fixture
def sync_client(app: Any) -> TestClient:
    """Sync test client (for simple GET endpoints)."""
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
async def async_client(app: Any) -> AsyncClient:
    """Async test client for full async tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mock_agent_run(app: Any) -> Any:
    """Patch agent.run on every agent in the registry with an AsyncMock.

    Tests that call POST /chat should set mock_agent_run.return_value to
    a MagicMock with a .text attribute before making requests.
    """
    registry = app.state.registry
    # Collect all real Agent objects in the registry
    agents = list(registry._agents.values())  # noqa: SLF001
    mocks: list[Any] = []
    patches: list[Any] = []
    mock_run = AsyncMock()
    for agent_obj in agents:
        p = patch.object(agent_obj, "run", new=mock_run)
        p.start()
        patches.append(p)
        mocks.append(mock_run)
    yield mock_run
    for p in patches:
        p.stop()
