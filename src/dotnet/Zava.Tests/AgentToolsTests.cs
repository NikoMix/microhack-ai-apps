using System.Text.Json;
using FluentAssertions;
using Zava.Api.Data;
using Zava.Api.Data.Models;

namespace Zava.Tests;

/// <summary>
/// Tests for <see cref="ZavaDataStore"/> — verifies in-memory data operations
/// and search helpers without any network calls.
/// </summary>
public sealed class AgentToolsTests : IDisposable
{
    private readonly string _tmpDir;

    public AgentToolsTests()
    {
        _tmpDir = Path.Combine(Path.GetTempPath(), $"zava-tests-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_tmpDir);
        Directory.CreateDirectory(Path.Combine(_tmpDir, "policies"));
        WriteTestData();
    }

    public void Dispose() => Directory.Delete(_tmpDir, recursive: true);

    // ── Empty store ───────────────────────────────────────────────────────────

    [Fact]
    public void EmptyStore_AllCollectionsEmpty()
    {
        var store = new ZavaDataStore();
        store.Products.Should().BeEmpty();
        store.Orders.Should().BeEmpty();
        store.Customers.Should().BeEmpty();
        store.Reviews.Should().BeEmpty();
        store.KnowledgeDocs.Should().BeEmpty();
    }

    [Fact]
    public void EmptyStore_SearchProducts_ReturnsEmpty()
    {
        var store = new ZavaDataStore();
        store.SearchProducts("running", topK: 5).Should().BeEmpty();
    }

    [Fact]
    public void EmptyStore_SearchKnowledge_ReturnsEmpty()
    {
        var store = new ZavaDataStore();
        store.SearchKnowledge("return policy", queryEmbedding: null, topK: 3).Should().BeEmpty();
    }

    // ── Loaded store ──────────────────────────────────────────────────────────

    [Fact]
    public void Load_PopulatesAllCollections()
    {
        var store = new ZavaDataStore();
        store.Load(_tmpDir);
        store.Products.Should().NotBeEmpty();
        store.Orders.Should().NotBeEmpty();
        store.Customers.Should().NotBeEmpty();
        store.Reviews.Should().NotBeEmpty();
        store.KnowledgeDocs.Should().NotBeEmpty();
    }

    [Fact]
    public void SearchProducts_MatchesBySmartFeature()
    {
        var store = LoadedStore();
        var results = store.SearchProducts("heart-rate", topK: 5);
        results.Should().NotBeEmpty();
    }

    [Fact]
    public void SearchProducts_MatchesByCategory()
    {
        var store = LoadedStore();
        var results = store.SearchProducts("running", topK: 5);
        results.Should().NotBeEmpty();
    }

    [Fact]
    public void SearchProducts_RespectsTopKLimit()
    {
        var store = LoadedStore();
        // Both products match "zava"
        var results = store.SearchProducts("zava", topK: 1);
        results.Count.Should().BeLessThanOrEqualTo(1);
    }

    [Fact]
    public void GetProduct_ExistingId_ReturnsProduct()
    {
        var store = LoadedStore();
        var product = store.GetProduct("ZAVA-RUN-001");
        product.Should().NotBeNull();
        product!.Id.Should().Be("ZAVA-RUN-001");
    }

    [Fact]
    public void GetProduct_MissingId_ReturnsNull()
    {
        var store = LoadedStore();
        store.GetProduct("NOTEXIST").Should().BeNull();
    }

    [Fact]
    public void GetOrder_ExistingId_ReturnsOrder()
    {
        var store = LoadedStore();
        var order = store.GetOrder("ORD-001");
        order.Should().NotBeNull();
        order!.OrderId.Should().Be("ORD-001");
    }

    [Fact]
    public void GetOrder_MissingId_ReturnsNull()
    {
        var store = LoadedStore();
        store.GetOrder("NOTEXIST").Should().BeNull();
    }

    [Fact]
    public void GetReviews_NullProductId_ReturnsAllReviews()
    {
        var store = LoadedStore();
        store.GetReviews(null).Count.Should().BeGreaterThan(0);
    }

    [Fact]
    public void GetReviews_FiltersByProductId()
    {
        var store = LoadedStore();
        var reviews = store.GetReviews("ZAVA-RUN-001");
        reviews.All(r => r.ProductId == "ZAVA-RUN-001").Should().BeTrue();
    }

    // ── Knowledge search ──────────────────────────────────────────────────────

    [Fact]
    public void SearchKnowledge_KeywordFallback_FindsMatchingDoc()
    {
        var store = LoadedStore();
        var results = store.SearchKnowledge("return items", queryEmbedding: null, topK: 3);
        results.Should().NotBeEmpty();
        results.Any(d => d.Content.Contains("return", StringComparison.OrdinalIgnoreCase)).Should().BeTrue();
    }

    [Fact]
    public void SearchKnowledge_WithEmbedding_UsesCosineSimilarity()
    {
        var store = LoadedStore();
        // Assign a synthetic embedding to one doc
        var doc = store.KnowledgeDocs[0];
        var syntheticEmbedding = new float[3] { 1f, 0f, 0f };
        store.SetKnowledgeEmbeddings(new Dictionary<string, float[]> { [doc.Id] = syntheticEmbedding });

        // Query with same vector should rank that doc highest
        var results = store.SearchKnowledge("anything", queryEmbedding: syntheticEmbedding, topK: 1);
        results.Should().NotBeEmpty();
        results[0].Id.Should().Be(doc.Id);
    }

    // ── Serialisation round-trip ──────────────────────────────────────────────

    [Fact]
    public void Product_SerialiseRoundTrip()
    {
        var p = new Product
        {
            Id = "ZAVA-001",
            Name = "ZavaRun X3",
            Category = "running",
            Subcategory = "trail",
            Price = 149.99m,
            SmartFeatures = ["heart-rate monitor", "GPS"],
            Description = "High performance trail running shoes.",
            InStock = 50,
            Rating = 4.7,
        };

        var opts = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
        var json = JsonSerializer.Serialize(p, opts);
        var p2 = JsonSerializer.Deserialize<Product>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
        p2.Should().NotBeNull();
        p2!.Id.Should().Be("ZAVA-001");
        p2.SmartFeatures.Should().Contain("GPS");
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private ZavaDataStore LoadedStore()
    {
        var store = new ZavaDataStore();
        store.Load(_tmpDir);
        return store;
    }

    private void WriteTestData()
    {
        var opts = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };

        var products = new List<object>
        {
            new { id = "ZAVA-RUN-001", name = "ZavaRun Pro", category = "running",
                  subcategory = "road", price = 159.99, currency = "USD",
                  sizes = new[] { "S", "M", "L" }, colors = new[] { "black" },
                  smartFeatures = new[] { "heart-rate monitor", "GPS" },
                  batteryHours = 12, washCycles = 100, inStock = 200,
                  description = "Advanced running shorts with biometric sensors.", rating = 4.8 },
            new { id = "ZAVA-YOG-001", name = "ZavaYoga Flow", category = "yoga",
                  subcategory = "studio", price = 89.99, currency = "USD",
                  sizes = new[] { "XS", "S", "M" }, colors = new[] { "navy" },
                  smartFeatures = new[] { "stretch sensor" },
                  batteryHours = 8, washCycles = 200, inStock = 150,
                  description = "Premium yoga pants with movement tracking.", rating = 4.5 },
        };
        File.WriteAllText(Path.Combine(_tmpDir, "products.json"),
            JsonSerializer.Serialize(products, opts));

        var orders = new List<object>
        {
            new { orderId = "ORD-001", customer = "C001", customerName = "Alice Smith",
                  status = "shipped", placedOn = "2025-01-15",
                  items = new[] { new { productId = "ZAVA-RUN-001", qty = 1, size = "M", color = "black" } },
                  total = 159.99, shipTo = "123 Main St, Seattle WA" },
        };
        File.WriteAllText(Path.Combine(_tmpDir, "orders.json"),
            JsonSerializer.Serialize(orders, opts));

        var customers = new List<object>
        {
            new { id = "C001", name = "Alice Smith", type = "individual", industry = "tech",
                  associationType = "direct", primaryPillars = new[] { "performance", "recovery" },
                  description = "Health-focused runner." },
        };
        File.WriteAllText(Path.Combine(_tmpDir, "customers.json"),
            JsonSerializer.Serialize(customers, opts));

        var reviews = new List<object>
        {
            new { productId = "ZAVA-RUN-001", customer = "C001", rating = 5,
                  title = "Best running shorts!", text = "The heart-rate monitoring is incredible." },
        };
        File.WriteAllText(Path.Combine(_tmpDir, "reviews.json"),
            JsonSerializer.Serialize(reviews, opts));

        // Policy document for knowledge store
        File.WriteAllText(Path.Combine(_tmpDir, "policies", "returns.md"), """
            # Return Policy

            Customers may return items within 30 days of purchase.
            Items must be in original condition with tags attached.
            Smart-apparel firmware updates do not affect return eligibility.
            """);
    }
}

