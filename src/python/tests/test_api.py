"""
HTTP API integration tests.

These tests exercise the full request/response cycle with a mocked LLM.
Agent.run() is patched on all registry agents so no real LLM calls are made.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient


def _make_agent_response(text: str = "Test reply from mock LLM.") -> MagicMock:
    """Build a mock AgentResponse with .text attribute."""
    result = MagicMock()
    result.text = text
    return result


# ── GET /health ───────────────────────────────────────────────────────────────


class TestHealth:
    def test_health_returns_ok(self, sync_client: Any) -> None:
        """GET /health returns 200 with status=ok."""
        response = sync_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_no_auth_required(self, sync_client: Any) -> None:
        """GET /health does not require any authentication."""
        # No headers — should still work
        response = sync_client.get("/health")
        assert response.status_code == 200


# ── GET /agents ───────────────────────────────────────────────────────────────


class TestAgents:
    def test_agents_returns_list(self, sync_client: Any) -> None:
        """GET /agents returns a non-empty list."""
        response = sync_client.get("/agents")
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) > 0

    def test_agents_contain_required_keys(self, sync_client: Any) -> None:
        """Each agent entry has key, name, description."""
        response = sync_client.get("/agents")
        agents = response.json()
        for agent in agents:
            assert "key" in agent, f"Missing 'key' in {agent}"
            assert "name" in agent, f"Missing 'name' in {agent}"
            assert "description" in agent, f"Missing 'description' in {agent}"

    def test_agents_includes_all_five(self, sync_client: Any) -> None:
        """All five Zava agents are listed."""
        response = sync_client.get("/agents")
        keys = {a["key"] for a in response.json()}
        assert "concierge" in keys
        assert "merchandiser" in keys
        assert "operations" in keys
        assert "trust" in keys
        assert "orchestrator" in keys

    def test_agents_no_auth_required(self, sync_client: Any) -> None:
        """GET /agents does not require authentication."""
        response = sync_client.get("/agents")
        assert response.status_code == 200


# ── POST /chat ────────────────────────────────────────────────────────────────


class TestChat:
    @pytest.mark.asyncio
    async def test_chat_returns_required_fields(
        self, async_client: AsyncClient, mock_agent_run: AsyncMock
    ) -> None:
        """POST /chat response contains reply, agent, citations, traceId."""
        mock_agent_run.return_value = _make_agent_response("The returns policy is 45 days.")
        response = await async_client.post(
            "/chat",
            json={"message": "What is the returns policy?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "agent" in data
        assert "citations" in data
        assert "traceId" in data

    @pytest.mark.asyncio
    async def test_chat_reply_is_string(
        self, async_client: AsyncClient, mock_agent_run: AsyncMock
    ) -> None:
        """POST /chat reply field is a non-empty string."""
        mock_agent_run.return_value = _make_agent_response("Here is the information.")
        response = await async_client.post(
            "/chat",
            json={"message": "Tell me about running shirts"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0

    @pytest.mark.asyncio
    async def test_chat_with_explicit_agent(
        self, async_client: AsyncClient, mock_agent_run: AsyncMock
    ) -> None:
        """POST /chat with explicit agent key routes to that agent."""
        mock_agent_run.return_value = _make_agent_response("The Pulse Running Shirt is our top.")
        response = await async_client.post(
            "/chat",
            json={"message": "Show me running products", "agent": "merchandiser"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "agent" in data
        assert isinstance(data["agent"], str)

    @pytest.mark.asyncio
    async def test_chat_citations_is_list(
        self, async_client: AsyncClient, mock_agent_run: AsyncMock
    ) -> None:
        """POST /chat citations field is always a list."""
        mock_agent_run.return_value = _make_agent_response("The warranty is 2 years.")
        response = await async_client.post(
            "/chat",
            json={"message": "What is the warranty?", "agent": "trust"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["citations"], list)

    @pytest.mark.asyncio
    async def test_chat_trace_id_is_32_char_hex(
        self, async_client: AsyncClient, mock_agent_run: AsyncMock
    ) -> None:
        """POST /chat traceId is a 32-character hex string."""
        mock_agent_run.return_value = _make_agent_response("Order ZO-100431 has been delivered.")
        response = await async_client.post(
            "/chat",
            json={"message": "Status of order ZO-100431"},
        )

        assert response.status_code == 200
        trace_id = response.json()["traceId"]
        assert isinstance(trace_id, str)
        assert len(trace_id) == 32
        # Must be valid hex
        int(trace_id, 16)

    @pytest.mark.asyncio
    async def test_chat_missing_message_returns_422(self, async_client: AsyncClient) -> None:
        """POST /chat with missing message field returns 422 Unprocessable Entity."""
        response = await async_client.post("/chat", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_empty_message_returns_422(self, async_client: AsyncClient) -> None:
        """POST /chat with empty string message returns 422."""
        response = await async_client.post("/chat", json={"message": ""})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_session_id_accepted(
        self, async_client: AsyncClient, mock_agent_run: AsyncMock
    ) -> None:
        """POST /chat accepts sessionId field without error."""
        mock_agent_run.return_value = _make_agent_response("Follow-up response.")
        response = await async_client.post(
            "/chat",
            json={"message": "Follow-up question", "sessionId": "test-session-abc"},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_chat_camelcase_session_id_alias(
        self, async_client: AsyncClient, mock_agent_run: AsyncMock
    ) -> None:
        """POST /chat accepts sessionId (camelCase) as per build contract."""
        mock_agent_run.return_value = _make_agent_response("Response.")
        response = await async_client.post(
            "/chat",
            json={"message": "Hello", "sessionId": "sess-xyz"},
        )

        assert response.status_code == 200


# ── Schema validation tests ───────────────────────────────────────────────────


class TestSchemas:
    def test_chat_request_validates_message(self) -> None:
        """ChatRequest requires a non-empty message."""
        import pydantic

        from app.api.schemas import ChatRequest

        with pytest.raises(pydantic.ValidationError):
            ChatRequest(message="")

    def test_chat_response_trace_id_alias(self) -> None:
        """ChatResponse serialises traceId correctly (camelCase alias)."""
        from app.api.schemas import ChatResponse

        resp = ChatResponse.model_validate(
            {
                "reply": "hello",
                "agent": "concierge",
                "citations": [],
                "traceId": "a" * 32,
            }
        )
        data = resp.model_dump(by_alias=True)
        assert "traceId" in data
        assert data["traceId"] == "a" * 32

    def test_agent_info_fields(self) -> None:
        """AgentInfo model has key, name, description."""
        from app.api.schemas import AgentInfo

        info = AgentInfo(key="concierge", name="Zava Concierge", description="Customer support")
        assert info.key == "concierge"
