using System.Collections.Concurrent;
using System.Diagnostics;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

namespace Zava.Api.Agents;

/// <summary>
/// Result returned from an agent run, containing the reply text, citations,
/// and the OTel trace ID of the span that covered the run.
/// </summary>
public sealed class AgentRunResult
{
    public string Reply { get; init; } = string.Empty;
    public List<string> Citations { get; init; } = [];
    public string TraceId { get; init; } = string.Empty;
}

/// <summary>
/// Abstract base for all Zava agents. Manages per-session <see cref="AgentSession"/>
/// objects and exposes a uniform <see cref="RunAsync"/> / <see cref="RunStreamingAsync"/> API.
/// </summary>
public abstract class ZavaAgentBase
{
    // ── Identity ──────────────────────────────────────────────────────────────

    /// <summary>Short agent key used in the HTTP API (e.g. "concierge").</summary>
    public abstract string Key { get; }

    /// <summary>Human-readable display name.</summary>
    public abstract string Name { get; }

    /// <summary>One-sentence description of the agent's purpose.</summary>
    public abstract string Description { get; }

    // ── Session cache ─────────────────────────────────────────────────────────

    // Agent is created once; sessions are cached per conversation ID.
    protected abstract AIAgent Agent { get; }

    /// <summary>Exposes the underlying <see cref="AIAgent"/> as a function tool for orchestration.</summary>
    public AIFunction AsAIFunction() => Agent.AsAIFunction();

    private readonly ConcurrentDictionary<string, AgentSession> _sessions = new();

    private async ValueTask<AgentSession?> GetSessionAsync(
        string? sessionId,
        CancellationToken ct)
    {
        if (sessionId is null)
        {
            return null;
        }

        if (_sessions.TryGetValue(sessionId, out var existing))
        {
            return existing;
        }

        // Create a fresh session; the session object carries the conversation history.
        // We cache it so subsequent turns with the same sessionId reuse it.
        var newSession = await Agent.CreateSessionAsync(ct);
        _sessions[sessionId] = newSession;
        return newSession;
    }

    // ── Public API ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Runs the agent with the given message and returns the complete reply.
    /// </summary>
    public virtual async Task<AgentRunResult> RunAsync(
        string message,
        string? sessionId = null,
        CancellationToken ct = default)
    {
        var session = await GetSessionAsync(sessionId, ct);
        var response = session is null
            ? await Agent.RunAsync(message, cancellationToken: ct)
            : await Agent.RunAsync(message, session, cancellationToken: ct);

        var traceId = Activity.Current?.TraceId.ToString() ?? string.Empty;
        return new AgentRunResult
        {
            Reply = response.Text ?? string.Empty,
            Citations = ExtractCitations(response),
            TraceId = traceId,
        };
    }

    /// <summary>
    /// Streams agent output as text chunks. Used for SSE responses.
    /// </summary>
    public virtual async IAsyncEnumerable<string> RunStreamingAsync(
        string message,
        string? sessionId = null,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken ct = default)
    {
        var session = await GetSessionAsync(sessionId, ct);
        var stream = session is null
            ? Agent.RunStreamingAsync(message, cancellationToken: ct)
            : Agent.RunStreamingAsync(message, session, cancellationToken: ct);

        await foreach (var update in stream.WithCancellation(ct))
        {
            if (!string.IsNullOrEmpty(update.Text))
            {
                yield return update.Text;
            }
        }
    }

    // ── Citations helper ──────────────────────────────────────────────────────

    /// <summary>
    /// Scans message tool results for any "_source" markers inserted by agent tools.
    /// </summary>
    private static List<string> ExtractCitations(AgentResponse response)
    {
        var citations = new List<string>();
        foreach (var msg in response.Messages)
        {
            foreach (var content in msg.Contents)
            {
                if (content is Microsoft.Extensions.AI.TextContent tc
                    && tc.Text is not null
                    && tc.Text.Contains("\"_source\"", StringComparison.Ordinal))
                {
                    // Attempt to extract source fields using simple JSON parsing
                    try
                    {
                        using var doc = System.Text.Json.JsonDocument.Parse(tc.Text);
                        if (doc.RootElement.TryGetProperty("_source", out var src))
                        {
                            var s = src.GetString();
                            if (!string.IsNullOrEmpty(s))
                            {
                                citations.Add(s);
                            }
                        }
                    }
                    catch (System.Text.Json.JsonException)
                    {
                        // Not JSON — skip
                    }
                }
            }
        }
        return citations;
    }
}
