using Microsoft.Extensions.AI;
using Zava.Api.Inference;

namespace Zava.Api.Data;

/// <summary>
/// Seeds the <see cref="ZavaDataStore"/> at startup:
/// 1. Loads JSON + markdown files from the <c>data/</c> directory.
/// 2. Generates 1536-dim embeddings for knowledge documents so RAG works.
///
/// In Azure mode (Cosmos DB + PostgreSQL pgvector), this would also push records
/// to those stores. For GitHub mode the in-memory store suffices.
/// </summary>
public sealed class ZavaSeeder
{
    private readonly ZavaDataStore _store;
    private readonly IInferenceFactory _inference;
    private readonly IConfiguration _config;
    private readonly ILogger<ZavaSeeder> _logger;

    public ZavaSeeder(
        ZavaDataStore store,
        IInferenceFactory inference,
        IConfiguration config,
        ILogger<ZavaSeeder> logger)
    {
        _store = store;
        _inference = inference;
        _config = config;
        _logger = logger;
    }

    /// <summary>
    /// Runs the seeding pipeline: load data → embed knowledge docs.
    /// Safe to call multiple times (idempotent).
    /// </summary>
    public async Task SeedAsync(CancellationToken ct = default)
    {
        var dataPath = ResolveDataPath();
        _logger.LogInformation("Seeding Zava data store from {DataPath}", dataPath);

        // 1 — Load raw data files
        _store.Load(dataPath);
        _logger.LogInformation(
            "Loaded {Products} products, {Orders} orders, {Reviews} reviews, {Docs} knowledge chunks",
            _store.Products.Count, _store.Orders.Count, _store.Reviews.Count, _store.KnowledgeDocs.Count);

        // 2 — Embed knowledge documents for vector search
        await EmbedKnowledgeDocsAsync(ct);

        _logger.LogInformation("Zava data store seeding complete");
    }

    private async Task EmbedKnowledgeDocsAsync(CancellationToken ct)
    {
        var docs = _store.KnowledgeDocs.Where(d => d.Embedding is null).ToList();
        if (docs.Count == 0)
        {
            _logger.LogDebug("All knowledge docs already have embeddings — skipping");
            return;
        }

        _logger.LogInformation("Generating embeddings for {Count} knowledge document chunks…", docs.Count);
        var embeddings = new Dictionary<string, float[]>(docs.Count);

        using var generator = _inference.CreateEmbeddingGenerator();

        // Batch in groups of 10 to avoid rate-limit issues on GitHub Models
        const int batchSize = 10;
        for (int i = 0; i < docs.Count; i += batchSize)
        {
            var batch = docs.Skip(i).Take(batchSize).ToList();
            var texts = batch.Select(d => d.Content).ToList();
            try
            {
                var vectors = await generator.GenerateAsync(texts, cancellationToken: ct);
                for (int j = 0; j < batch.Count; j++)
                {
                    embeddings[batch[j].Id] = vectors[j].Vector.Span.ToArray();
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to embed batch {Batch}/{Total}; skipping — keyword search will be used",
                    i / batchSize + 1, (docs.Count + batchSize - 1) / batchSize);
            }

            // Small delay to respect GitHub Models rate limits
            if (i + batchSize < docs.Count)
            {
                await Task.Delay(200, ct);
            }
        }

        _store.SetKnowledgeEmbeddings(embeddings);
        _logger.LogInformation("Embedded {Count}/{Total} knowledge document chunks", embeddings.Count, docs.Count);
    }

    /// <summary>
    /// Resolves the data directory path:
    /// 1. DATA_PATH env var.
    /// 2. Well-known relative paths from the working directory.
    /// 3. Walks up looking for the data/ folder (dev / Docker fallbacks).
    /// </summary>
    private string ResolveDataPath()
    {
        var envPath = _config["DATA_PATH"];
        if (!string.IsNullOrEmpty(envPath) && Directory.Exists(envPath))
        {
            return envPath;
        }

        // Try relative paths from working directory
        var candidates = new[]
        {
            "data",                           // running from repo root
            "../../../data",                   // running from src/dotnet/Zava.Api/
            "../../../../data",                // running from bin/Debug/net10.0/
        };

        foreach (var rel in candidates)
        {
            var path = Path.GetFullPath(rel);
            if (Directory.Exists(path) && File.Exists(Path.Combine(path, "products.json")))
            {
                return path;
            }
        }

        // Walk up from assembly location
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null)
        {
            var candidate = Path.Combine(dir.FullName, "data");
            if (Directory.Exists(candidate) && File.Exists(Path.Combine(candidate, "products.json")))
            {
                return candidate;
            }

            dir = dir.Parent;
        }

        throw new InvalidOperationException(
            "Cannot locate the 'data/' directory. Set the DATA_PATH environment variable.");
    }
}
