namespace Zava.Api.Models;

// ── Inbound ──────────────────────────────────────────────────────────────────

/// <summary>Request body for POST /chat and POST /chat/stream.</summary>
public sealed class ChatRequest
{
    /// <summary>User message text.</summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Target agent key (concierge | merchandiser | operations | trust | orchestrator).
    /// Omit to let the orchestrator triage.
    /// </summary>
    public string? Agent { get; set; }

    /// <summary>
    /// Conversation session identifier for multi-turn support.
    /// Generate client-side and re-use across turns.
    /// </summary>
    public string? SessionId { get; set; }
}

// ── Outbound ─────────────────────────────────────────────────────────────────

/// <summary>Response body for POST /chat (non-streaming).</summary>
public sealed class ChatResponse
{
    /// <summary>Agent's reply text.</summary>
    public string Reply { get; set; } = string.Empty;

    /// <summary>Key of the agent that produced the reply.</summary>
    public string Agent { get; set; } = string.Empty;

    /// <summary>Source citations extracted from tool results.</summary>
    public List<string> Citations { get; set; } = [];

    /// <summary>OpenTelemetry trace ID for distributed tracing.</summary>
    public string TraceId { get; set; } = string.Empty;
}

/// <summary>Descriptor returned by GET /agents.</summary>
public sealed class AgentInfo
{
    public string Key { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
}
