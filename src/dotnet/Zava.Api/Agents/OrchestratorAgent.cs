using Microsoft.Agents.AI;
using Zava.Api.Inference;

namespace Zava.Api.Agents;

/// <summary>
/// Orchestrator agent: triages incoming requests and routes them to the appropriate
/// specialist agent (concierge, merchandiser, operations, trust) using the
/// Agent Framework's agent-as-function pattern.
///
/// Each sub-agent is converted to a function tool via <c>.AsAIFunction()</c>,
/// so the LLM decides which to call based on the message intent.
/// </summary>
public sealed class OrchestratorAgent : ZavaAgentBase
{
    public override string Key => "orchestrator";
    public override string Name => "Orchestrator";
    public override string Description =>
        "Routes requests to the best specialist: concierge (orders/returns/product Q&A), merchandiser (recommendations/reviews), operations (inventory/supply-chain), or trust (compliance/safety).";

    protected override AIAgent Agent { get; }

    private const string SystemPrompt = """
        You are the Zava AI Platform Orchestrator.
        Your sole job is to route customer and internal requests to the correct specialist agent.

        Routing guide:
        - Orders, returns, shipping, product Q&A, policy questions → Concierge
        - Product search, recommendations, reviews, sales trends → Merchandiser
        - Inventory, supply chain, supplier docs, restock → Operations
        - Content safety checks, compliance, audit evidence, policy governance → Trust

        Call exactly one specialist for each request. Pass the user's message verbatim to the specialist.
        Return the specialist's response directly without modification.
        """;

    public OrchestratorAgent(
        IInferenceFactory inference,
        ConciergeAgent concierge,
        MerchandiserAgent merchandiser,
        OperationsAgent operations,
        TrustAgent trust)
    {
        // Convert each specialist agent into a function tool so the LLM can route to it.
        Agent = inference.CreateAgent(
            name: Name,
            description: Description,
            instructions: SystemPrompt,
            tools:
            [
                concierge.AsAIFunction(),
                merchandiser.AsAIFunction(),
                operations.AsAIFunction(),
                trust.AsAIFunction(),
            ]);
    }
}
