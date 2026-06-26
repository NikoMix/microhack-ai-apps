// A chunked, embedded policy / knowledge document for RAG
namespace Zava.Api.Data.Models;

public sealed class KnowledgeDocument
{
    /// <summary>Unique identifier (e.g. "policies/returns.md:chunk-0").</summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>Human-readable title (e.g. "Zava Returns Policy").</summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>Original source file path relative to the data directory.</summary>
    public string Source { get; set; } = string.Empty;

    /// <summary>Text chunk that was embedded.</summary>
    public string Content { get; set; } = string.Empty;

    /// <summary>1536-dimensional embedding vector (text-embedding-3-small).</summary>
    public float[]? Embedding { get; set; }
}
