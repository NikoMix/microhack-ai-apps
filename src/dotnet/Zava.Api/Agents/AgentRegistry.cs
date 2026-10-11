using Zava.Api.Models;

namespace Zava.Api.Agents;

/// <summary>
/// Holds all registered Zava agents and dispatches requests by agent key.
/// Registered as a singleton in DI. Agents are injected as an enumerable
/// so callers can add or replace them in tests.
/// </summary>
public sealed class AgentRegistry
{
    private readonly Dictionary<string, ZavaAgentBase> _agents;

    public AgentRegistry(IEnumerable<ZavaAgentBase> agents)
    {
        _agents = agents.ToDictionary(a => a.Key, StringComparer.OrdinalIgnoreCase);
    }

    /// <summary>Returns the list of agent descriptors for <c>GET /agents</c>.</summary>
    public IReadOnlyList<AgentInfo> GetAgentInfos() =>
        _agents.Values.Select(a => new AgentInfo
        {
            Key = a.Key,
            Name = a.Name,
            Description = a.Description,
        }).ToList();

    /// <summary>
    /// Resolves the correct agent for a request:
    /// - If <paramref name="agentKey"/> is null or "orchestrator" (or unknown), use the orchestrator.
    /// - Otherwise return the named agent.
    /// </summary>
    public ZavaAgentBase Resolve(string? agentKey)
    {
        if (agentKey is null || !_agents.TryGetValue(agentKey, out var agent))
        {
            return _agents["orchestrator"];
        }

        return agent;
    }
}
