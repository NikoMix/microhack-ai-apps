using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

namespace Zava.Api.Inference;

/// <summary>
/// Abstracts LLM chat and embedding creation.
/// Switch providers by setting <c>INFERENCE_PROVIDER</c> / <c>EMBEDDINGS_PROVIDER</c>.
/// </summary>
public interface IInferenceFactory
{
    /// <summary>Provider name (github | azure-openai | foundry).</summary>
    string InferenceProvider { get; }

    /// <summary>Embeddings provider name (github | azure-openai | foundry).</summary>
    string EmbeddingsProvider { get; }

    /// <summary>
    /// Creates a new <see cref="AIAgent"/> backed by the configured chat provider.
    /// </summary>
    /// <param name="name">Agent display name.</param>
    /// <param name="description">One-sentence description of the agent (used for tool routing).</param>
    /// <param name="instructions">System prompt / persona instructions.</param>
    /// <param name="tools">Optional function tools to register with the agent.</param>
    AIAgent CreateAgent(
        string name,
        string description,
        string instructions,
        IList<AITool>? tools = null);

    /// <summary>
    /// Returns an embedding generator for 1536-dim vectors (text-embedding-3-small).
    /// </summary>
    IEmbeddingGenerator<string, Embedding<float>> CreateEmbeddingGenerator();
}

