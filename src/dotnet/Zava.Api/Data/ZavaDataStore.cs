using System.Text.Json;
using Zava.Api.Data.Models;

namespace Zava.Api.Data;

/// <summary>
/// In-memory Zava data store loaded from the <c>data/</c> seed files.
/// In Azure mode the same interface can be backed by Cosmos DB + pgvector.
/// </summary>
public sealed class ZavaDataStore
{
    // ── raw collections ──────────────────────────────────────────────────────
    public IReadOnlyList<Product> Products { get; private set; } = [];
    public IReadOnlyList<Order> Orders { get; private set; } = [];
    public IReadOnlyList<Customer> Customers { get; private set; } = [];
    public IReadOnlyList<Review> Reviews { get; private set; } = [];
    public IReadOnlyList<KnowledgeDocument> KnowledgeDocs { get; private set; } = [];

    // raw supplier doc content keyed by filename (no extension)
    private readonly Dictionary<string, string> _supplierDocs = new(StringComparer.OrdinalIgnoreCase);

    // ── query helpers ─────────────────────────────────────────────────────────

    public Product? GetProduct(string id) =>
        Products.FirstOrDefault(p => string.Equals(p.Id, id, StringComparison.OrdinalIgnoreCase));

    public Order? GetOrder(string id) =>
        Orders.FirstOrDefault(o => string.Equals(o.OrderId, id, StringComparison.OrdinalIgnoreCase));

    public IReadOnlyList<Review> GetReviews(string? productId = null) =>
        productId is null
            ? Reviews
            : Reviews.Where(r => string.Equals(r.ProductId, productId, StringComparison.OrdinalIgnoreCase)).ToList();

    /// <summary>
    /// Simple keyword search over product names, descriptions, categories and smart features.
    /// Returns up to <paramref name="topK"/> results sorted by relevance score.
    /// </summary>
    public IReadOnlyList<Product> SearchProducts(string query, int topK = 5)
    {
        if (string.IsNullOrWhiteSpace(query))
        {
            return Products.Take(topK).ToList();
        }

        var terms = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        return Products
            .Select(p => (product: p, score: Score(p, terms)))
            .Where(x => x.score > 0)
            .OrderByDescending(x => x.score)
            .Take(topK)
            .Select(x => x.product)
            .ToList();
    }

    private static int Score(Product p, string[] terms)
    {
        var blob = $"{p.Name} {p.Description} {p.Category} {p.Subcategory} {string.Join(' ', p.SmartFeatures)}";
        return terms.Count(t => blob.Contains(t, StringComparison.OrdinalIgnoreCase));
    }

    /// <summary>
    /// Semantic-style search over knowledge documents.
    /// If <paramref name="queryEmbedding"/> is supplied and docs have pre-computed embeddings,
    /// uses cosine similarity; otherwise falls back to keyword matching.
    /// </summary>
    public IReadOnlyList<KnowledgeDocument> SearchKnowledge(
        string query,
        float[]? queryEmbedding = null,
        int topK = 3)
    {
        if (queryEmbedding is { Length: > 0 })
        {
            var docsWithEmbeddings = KnowledgeDocs.Where(d => d.Embedding is { Length: > 0 }).ToList();
            if (docsWithEmbeddings.Count > 0)
            {
                return docsWithEmbeddings
                    .Select(d => (doc: d, score: CosineSimilarity(queryEmbedding, d.Embedding!)))
                    .OrderByDescending(x => x.score)
                    .Take(topK)
                    .Select(x => x.doc)
                    .ToList();
            }
        }

        // Keyword fallback
        var terms = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        return KnowledgeDocs
            .Select(d => (doc: d, score: terms.Count(t => d.Content.Contains(t, StringComparison.OrdinalIgnoreCase))))
            .Where(x => x.score > 0)
            .OrderByDescending(x => x.score)
            .Take(topK)
            .Select(x => x.doc)
            .ToList();
    }

    private static float CosineSimilarity(float[] a, float[] b)
    {
        if (a.Length != b.Length)
        {
            return 0f;
        }

        float dot = 0, magA = 0, magB = 0;
        for (int i = 0; i < a.Length; i++)
        {
            dot += a[i] * b[i];
            magA += a[i] * a[i];
            magB += b[i] * b[i];
        }
        return magA == 0 || magB == 0 ? 0f : dot / (MathF.Sqrt(magA) * MathF.Sqrt(magB));
    }

    /// <summary>Returns raw markdown content of a supplier document by filename (without extension).</summary>
    public string? GetSupplierDoc(string name) =>
        _supplierDocs.TryGetValue(name, out var content) ? content : null;

    public IReadOnlyList<string> SupplierDocNames => _supplierDocs.Keys.ToList();

    // ── loading ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Loads all seed data from the <paramref name="dataPath"/> directory.
    /// Embeddings are populated later via <see cref="SetKnowledgeEmbeddings"/>.
    /// </summary>
    public void Load(string dataPath)
    {
        var opts = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };

        Products = LoadJson<Product>(Path.Combine(dataPath, "products.json"), opts);
        Orders = LoadJson<Order>(Path.Combine(dataPath, "orders.json"), opts);
        Customers = LoadJson<Customer>(Path.Combine(dataPath, "customers.json"), opts);
        Reviews = LoadJson<Review>(Path.Combine(dataPath, "reviews.json"), opts);

        // Load policy documents as knowledge chunks
        var knowledgeDocs = new List<KnowledgeDocument>();
        var policiesDir = Path.Combine(dataPath, "policies");
        if (Directory.Exists(policiesDir))
        {
            foreach (var file in Directory.GetFiles(policiesDir, "*.md"))
            {
                var content = File.ReadAllText(file);
                var relPath = $"policies/{Path.GetFileName(file)}";
                knowledgeDocs.AddRange(ChunkDocument(relPath, content));
            }
        }
        KnowledgeDocs = knowledgeDocs;

        // Load supplier docs
        var suppliersDir = Path.Combine(dataPath, "suppliers");
        if (Directory.Exists(suppliersDir))
        {
            foreach (var file in Directory.GetFiles(suppliersDir, "*.md"))
            {
                var key = Path.GetFileNameWithoutExtension(file);
                _supplierDocs[key] = File.ReadAllText(file);
            }
        }
    }

    /// <summary>Stores the embedding vectors (from the seeder) into the knowledge documents.</summary>
    public void SetKnowledgeEmbeddings(IReadOnlyDictionary<string, float[]> embeddings)
    {
        foreach (var doc in KnowledgeDocs)
        {
            if (embeddings.TryGetValue(doc.Id, out var emb))
            {
                doc.Embedding = emb;
            }
        }
    }

    private static List<T> LoadJson<T>(string path, JsonSerializerOptions opts)
    {
        if (!File.Exists(path))
        {
            return [];
        }

        using var stream = File.OpenRead(path);
        return JsonSerializer.Deserialize<List<T>>(stream, opts) ?? [];
    }

    /// <summary>
    /// Splits a markdown document into ≤400-word chunks for embedding.
    /// Produces IDs like "policies/returns.md:chunk-0".
    /// </summary>
    private static IEnumerable<KnowledgeDocument> ChunkDocument(string relPath, string content)
    {
        // Title from first H1 or fallback to filename
        var lines = content.Split('\n');
        var title = lines.FirstOrDefault(l => l.StartsWith("# ", StringComparison.Ordinal))?.TrimStart('#').Trim()
                    ?? Path.GetFileNameWithoutExtension(relPath);

        // Split into ~400-word chunks on paragraph boundaries
        var paragraphs = content.Split("\n\n", StringSplitOptions.RemoveEmptyEntries);
        var chunks = new List<string>();
        var current = new System.Text.StringBuilder();
        int wordCount = 0;

        foreach (var para in paragraphs)
        {
            var paraWords = para.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length;
            if (wordCount + paraWords > 400 && current.Length > 0)
            {
                chunks.Add(current.ToString().Trim());
                current.Clear();
                wordCount = 0;
            }
            current.AppendLine(para);
            wordCount += paraWords;
        }
        if (current.Length > 0)
        {
            chunks.Add(current.ToString().Trim());
        }

        return chunks.Select((chunk, i) => new KnowledgeDocument
        {
            Id = $"{relPath}:chunk-{i}",
            Title = title,
            Source = relPath,
            Content = chunk,
        });
    }
}
