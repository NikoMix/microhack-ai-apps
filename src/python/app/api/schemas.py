"""
Pydantic schemas for the Zava HTTP API.

Defined in build-contract.md §4.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ── Request models ────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """POST /chat — chat with Zava agents."""

    message: str = Field(..., min_length=1, description="User message")
    agent: str | None = Field(
        default=None,
        description="Agent key (concierge/merchandiser/operations/trust). "
        "Omit to let the orchestrator decide.",
    )
    session_id: str | None = Field(
        default=None,
        alias="sessionId",
        description="Opaque session identifier for multi-turn conversations.",
    )

    model_config = {"populate_by_name": True}


# ── Response models ───────────────────────────────────────────────────────────


class Citation(BaseModel):
    """A knowledge source cited in a reply."""

    source: str = Field(..., description="Source identifier (file path, URL, or ID)")
    title: str = Field(..., description="Human-readable title of the source")
    excerpt: str = Field(default="", description="Relevant excerpt from the source")


class ChatResponse(BaseModel):
    """POST /chat — structured response from an agent."""

    reply: str = Field(..., description="Agent's natural-language reply")
    agent: str = Field(..., description="Key of the agent that produced the reply")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Knowledge sources grounding the reply",
    )
    trace_id: str = Field(
        ...,
        alias="traceId",
        description="OpenTelemetry trace ID for this request",
    )

    model_config = {"populate_by_name": True}


class AgentInfo(BaseModel):
    """Entry in GET /agents response."""

    key: str = Field(..., description="Unique agent key")
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="What this agent does")


class HealthResponse(BaseModel):
    """GET /health response."""

    status: str = Field(default="ok")
