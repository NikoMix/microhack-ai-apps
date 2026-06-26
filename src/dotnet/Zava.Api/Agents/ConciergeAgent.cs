using System.ComponentModel;
using System.Text.Json;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Zava.Api.Data;
using Zava.Api.Inference;

namespace Zava.Api.Agents;

/// <summary>
/// Concierge agent: customer support for order status, returns, and product Q&amp;A (RAG).
///
/// Tools: get_order, get_product, search_knowledge, create_return.
/// </summary>
public sealed class ConciergeAgent : ZavaAgentBase
{
    public override string Key => "concierge";
    public override string Name => "Concierge";
    public override string Description =>
        "Handles customer support: order status, return requests, and product Q&A backed by Zava knowledge docs.";

    protected override AIAgent Agent { get; }

    private readonly ZavaDataStore _data;
    private readonly IEmbeddingGenerator<string, Embedding<float>> _embeddingGen;

    private const string SystemPrompt = """
        You are the Zava Concierge — a friendly, knowledgeable customer support specialist for Zava,
        an intelligent athletic apparel company. Help customers with:
        - Order status and tracking
        - Return requests (follow the Zava returns policy)
        - Product questions and compatibility
        - Policy information (returns, warranty, sizing, care)

        Always look up real data using your tools before answering. Be concise but helpful.
        When citing policies or product specs, include the source so the customer can refer back to it.
        """;

    public ConciergeAgent(
        IInferenceFactory inference,
        ZavaDataStore data,
        IEmbeddingGenerator<string, Embedding<float>> embeddingGen)
    {
        _data = data;
        _embeddingGen = embeddingGen;
        Agent = inference.CreateAgent(
            name: Name,
            description: Description,
            instructions: SystemPrompt,
            tools:
            [
                AIFunctionFactory.Create(GetOrderAsync),
                AIFunctionFactory.Create(GetProductAsync),
                AIFunctionFactory.Create(SearchKnowledgeAsync),
                AIFunctionFactory.Create(CreateReturnAsync),
            ]);
    }

    // ── Tools ─────────────────────────────────────────────────────────────────

    [Description("Get the status and full details of a Zava customer order by order ID.")]
    private Task<string> GetOrderAsync(
        [Description("The Zava order ID (e.g. ZO-100431)")] string orderId)
    {
        var order = _data.GetOrder(orderId);
        if (order is null)
        {
            return Task.FromResult($"No order found with ID '{orderId}'. Please verify the order number.");
        }

        return Task.FromResult(JsonSerializer.Serialize(order, JsonOpts));
    }

    [Description("Look up Zava product details by product ID, including price, sizes, colors, and smart features.")]
    private Task<string> GetProductAsync(
        [Description("The Zava product ID (e.g. ZAVA-RUN-001)")] string productId)
    {
        var product = _data.GetProduct(productId);
        if (product is null)
        {
            return Task.FromResult($"No product found with ID '{productId}'.");
        }

        return Task.FromResult(JsonSerializer.Serialize(product, JsonOpts));
    }

    [Description("Search Zava knowledge base (policies, warranty, sizing, care guides) for information relevant to a customer question.")]
    private async Task<string> SearchKnowledgeAsync(
        [Description("The search query or customer question")] string query)
    {
        // Attempt vector search first; fall back to keyword if embedding fails
        float[]? queryEmb = null;
        try
        {
            var vec = await _embeddingGen.GenerateVectorAsync(query);
            queryEmb = vec.Span.ToArray();
        }
        catch
        {
            // GitHub Models may throttle; keyword fallback is acceptable
        }

        var docs = _data.SearchKnowledge(query, queryEmb, topK: 3);
        if (docs.Count == 0)
        {
            return "No relevant knowledge found for that query.";
        }

        var results = docs.Select(d => new
        {
            title = d.Title,
            content = d.Content,
            _source = d.Source,
        });
        return JsonSerializer.Serialize(results, JsonOpts);
    }

    [Description("Initiate a return request for a customer order. Returns a confirmation with next steps.")]
    private Task<string> CreateReturnAsync(
        [Description("The Zava order ID for the return")] string orderId,
        [Description("Reason for the return (e.g. defective, wrong item, change of mind)")] string reason)
    {
        var order = _data.GetOrder(orderId);
        if (order is null)
        {
            return Task.FromResult($"Cannot initiate return: order '{orderId}' not found.");
        }

        var returnRef = $"RET-{orderId}-{DateTime.UtcNow:yyyyMMddHHmm}";
        return Task.FromResult(JsonSerializer.Serialize(new
        {
            returnReference = returnRef,
            orderId,
            reason,
            status = "Initiated",
            nextSteps = "You will receive a prepaid return label via email within 24 hours. " +
                        "Drop the package at any carrier point within 14 days of label creation.",
            policyNote = "Refunds are processed within 5–7 business days after receipt.",
            _source = "policies/returns.md",
        }, JsonOpts));
    }

    private static readonly JsonSerializerOptions JsonOpts =
        new() { WriteIndented = false, PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
}
