"""
HTTP API routes for the Zava AI Agent Platform.

Routes (build-contract §4):
  GET  /health         → {"status": "ok"}
  GET  /agents         → list of {key, name, description}
  POST /chat           → {reply, agent, citations[], traceId}
  POST /chat/stream    → SSE token stream

The orchestrator is used when no agent key is supplied in the request.
All responses include a real OpenTelemetry traceId.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from agent_framework import AgentResponse, Message
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

from app.agents.concierge import get_citations, reset_citations
from app.api.schemas import AgentInfo, ChatRequest, ChatResponse, Citation, HealthResponse
from app.telemetry.otel import get_trace_id

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple in-memory session store: session_id → AgentSession
# In production, replace with Redis or Cosmos-backed persistence.
_session_store: dict[str, Any] = {}


# ── Dependency: pull the AgentRegistry from app.state ────────────────────────


def _registry(request: Request) -> Any:
    """FastAPI dependency: returns the AgentRegistry from app state."""
    return request.app.state.registry


# ── GET /health ───────────────────────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    """Returns ``{"status": "ok"}`` — used by load-balancers and Container Apps."""
    return HealthResponse(status="ok")


# ── GET /agents ───────────────────────────────────────────────────────────────


@router.get("/agents", response_model=list[AgentInfo], summary="List available agents")
async def list_agents(registry: Any = Depends(_registry)) -> list[AgentInfo]:
    """Returns the catalogue of Zava agents with their keys and descriptions."""
    return [AgentInfo(**m) for m in registry.metadata]


# ── POST /chat ────────────────────────────────────────────────────────────────


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to a Zava agent",
    status_code=status.HTTP_200_OK,
)
async def chat(
    body: ChatRequest,
    registry: Any = Depends(_registry),
) -> ChatResponse:
    """Route a chat message to the appropriate Zava agent.

    - If ``agent`` is omitted, the orchestrator triages to the right specialist.
    - Maintains conversation history per ``sessionId`` (in-memory).
    - Returns ``traceId`` from the active OpenTelemetry span.
    """
    agent = registry.get_or_orchestrator(body.agent)
    session_id = body.session_id or ""

    # Get or create per-session AgentSession for conversation history
    if session_id not in _session_store:
        _session_store[session_id] = agent.create_session(session_id=session_id or None)
    session = _session_store[session_id]

    # Reset citation accumulator for this request
    reset_citations()

    try:
        result: AgentResponse[Any] = await agent.run(
            messages=[Message("user", [body.message])],
            session=session,
        )
    except Exception as exc:
        logger.exception("Agent run failed for message: %s", body.message[:100])
        _handle_agent_error(exc)  # raises HTTPException

    # Extract reply text from the agent response
    reply: str = result.text or ""

    # Determine which agent answered (agent_id on the response if available)
    answered_by: str = agent.name or "orchestrator"

    # Collect citations accumulated during tool calls
    raw_citations = get_citations()
    citations = [
        Citation(
            source=c["source"],
            title=c["title"],
            excerpt=c.get("excerpt", ""),
        )
        for c in raw_citations
    ]

    return ChatResponse.model_validate(
        {
            "reply": reply,
            "agent": answered_by,
            "citations": citations,
            "traceId": get_trace_id(),
        }
    )


# ── POST /chat/stream ─────────────────────────────────────────────────────────


@router.post("/chat/stream", summary="Stream a chat response (SSE)")
async def chat_stream(
    body: ChatRequest,
    registry: Any = Depends(_registry),
) -> EventSourceResponse:
    """SSE streaming endpoint — yields tokens as they are generated.

    Each SSE event has:
    - ``data``: a JSON payload with ``token`` (incremental text) or
      ``done`` (true) + final ``reply``, ``agent``, ``citations``, ``traceId``.
    """
    agent = registry.get_or_orchestrator(body.agent)
    session_id = body.session_id or ""
    reset_citations()
    trace_id = get_trace_id()

    # Ensure session exists for streaming too
    if session_id not in _session_store:
        _session_store[session_id] = agent.create_session(session_id=session_id or None)
    session = _session_store[session_id]

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        try:
            # Use streaming run — returns a ResponseStream
            stream = agent.run(
                messages=[Message("user", [body.message])],
                session=session,
                stream=True,
            )

            collected_text = ""
            async for update in stream:
                # Each update may contain partial text
                token = getattr(update, "text", None)
                if token:
                    collected_text += token
                    yield {"data": json.dumps({"token": token})}

            # Emit the final done event
            final_response = await stream.get_final_response()
            final_reply = final_response.text or collected_text
            answered_by = agent.name or "orchestrator"
            citations = [
                {"source": c["source"], "title": c["title"], "excerpt": c.get("excerpt", "")}
                for c in get_citations()
            ]
            yield {
                "data": json.dumps(
                    {
                        "done": True,
                        "reply": final_reply,
                        "agent": answered_by,
                        "citations": citations,
                        "traceId": trace_id,
                    }
                )
            }

        except Exception as exc:
            logger.exception("Stream error")
            # Fallback: run non-streaming and simulate chunking
            try:
                result_fb: AgentResponse[Any] = await agent.run(
                    messages=[Message("user", [body.message])],
                )
                reply_fb = result_fb.text or ""
                for chunk in _chunk_text(reply_fb, chunk_size=30):
                    yield {"data": json.dumps({"token": chunk})}
                    await asyncio.sleep(0)
                yield {
                    "data": json.dumps(
                        {
                            "done": True,
                            "reply": reply_fb,
                            "agent": agent.name or "orchestrator",
                            "citations": [
                                {
                                    "source": c["source"],
                                    "title": c["title"],
                                    "excerpt": c.get("excerpt", ""),
                                }
                                for c in get_citations()
                            ],
                            "traceId": trace_id,
                        }
                    )
                }
            except Exception:
                yield {"data": json.dumps({"error": str(exc), "traceId": trace_id})}

    return EventSourceResponse(event_generator())


# ── Internal helpers ──────────────────────────────────────────────────────────


def _handle_agent_error(exc: Exception) -> None:
    """Convert agent errors to appropriate HTTP exceptions."""
    msg = str(exc).lower()
    if "token" in msg or "unauthorized" in msg or "401" in msg:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "LLM backend unavailable. "
                "In github mode, set GITHUB_TOKEN (PAT with models:read). "
                f"Original error: {exc}"
            ),
        ) from exc
    if "rate" in msg or "429" in msg:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit hit on LLM provider: {exc}",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Agent error: {exc}",
    ) from exc


def _chunk_text(text: str, chunk_size: int = 30) -> list[str]:
    """Split text into word-boundary chunks for simulated streaming."""
    words = text.split()
    chunks = []
    current: list[str] = []
    for word in words:
        current.append(word)
        if len(current) >= chunk_size:
            chunks.append(" ".join(current) + " ")
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks
