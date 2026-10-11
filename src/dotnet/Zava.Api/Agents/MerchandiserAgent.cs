using System.ComponentModel;
using System.Text.Json;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Zava.Api.Data;
using Zava.Api.Inference;

namespace Zava.Api.Agents;

/// <summary>
/// Merchandiser agent: product insights, recommendations, and review analysis.
///
/// Tools: search_products, get_reviews, sales_trends.
/// </summary>
public sealed class MerchandiserAgent : ZavaAgentBase
{
    public override string Key => "merchandiser";
    public override string Name => "Merchandiser";
    public override string Description =>
        "Provides product recommendations, search, review analysis, and sales trend insights for Zava's smart-apparel catalog.";

    protected override AIAgent Agent { get; }

    private readonly ZavaDataStore _data;

    private const string SystemPrompt = """
        You are the Zava Merchandiser — an expert in Zava's smart-apparel product catalog.
        Help customers and internal teams with:
        - Finding the right product for a use case or activity
        - Comparing products (features, price, ratings)
        - Summarising customer reviews and sentiment
        - Sales and inventory trend analysis

        Use your tools to retrieve live product and review data. Highlight smart features
        and Zava differentiators. Always recommend based on data, not assumptions.
        """;

    public MerchandiserAgent(IInferenceFactory inference, ZavaDataStore data)
    {
        _data = data;
        Agent = inference.CreateAgent(
            name: Name,
            description: Description,
            instructions: SystemPrompt,
            tools:
            [
                AIFunctionFactory.Create(SearchProductsAsync),
                AIFunctionFactory.Create(GetReviewsAsync),
                AIFunctionFactory.Create(SalesTrendsAsync),
            ]);
    }

    // ── Tools ─────────────────────────────────────────────────────────────────

    [Description("Search the Zava product catalog by activity, category, feature, or keyword.")]
    private Task<string> SearchProductsAsync(
        [Description("Search query (e.g. 'running heart-rate', 'recovery compression', 'eco lifestyle')")] string query)
    {
        var products = _data.SearchProducts(query, topK: 5);
        if (products.Count == 0)
        {
            return Task.FromResult("No products found matching that query.");
        }

        return Task.FromResult(JsonSerializer.Serialize(products, JsonOpts));
    }

    [Description("Retrieve customer reviews for a specific product or all products.")]
    private Task<string> GetReviewsAsync(
        [Description("Product ID to filter (e.g. ZAVA-RUN-001); omit to get all reviews")] string? productId = null)
    {
        var reviews = _data.GetReviews(productId);
        if (reviews.Count == 0)
        {
            return Task.FromResult(productId is null ? "No reviews yet." : $"No reviews for product '{productId}'.");
        }

        // Include average rating summary
        var avg = reviews.Average(r => r.Rating);
        var result = new
        {
            averageRating = Math.Round(avg, 1),
            totalReviews = reviews.Count,
            reviews,
            _source = productId is null ? "data/reviews.json" : $"reviews for {productId}",
        };
        return Task.FromResult(JsonSerializer.Serialize(result, JsonOpts));
    }

    [Description("Get sales trend data: top-selling categories, stock levels, and inventory health summary.")]
    private Task<string> SalesTrendsAsync()
    {
        var products = _data.Products;
        var categories = products
            .GroupBy(p => p.Category)
            .Select(g => new
            {
                category = g.Key,
                itemCount = g.Count(),
                avgRating = Math.Round(g.Average(p => p.Rating), 1),
                totalStock = g.Sum(p => p.InStock),
                priceRange = $"${g.Min(p => p.Price):F0}–${g.Max(p => p.Price):F0}",
            })
            .OrderByDescending(c => c.totalStock)
            .ToList();

        var topRated = products.OrderByDescending(p => p.Rating).Take(3)
            .Select(p => new { p.Id, p.Name, p.Rating });

        var lowStock = products.Where(p => p.InStock < 100)
            .Select(p => new { p.Id, p.Name, p.InStock });

        return Task.FromResult(JsonSerializer.Serialize(new
        {
            categorySummary = categories,
            topRated,
            lowStockAlerts = lowStock,
            _source = "data/products.json",
        }, JsonOpts));
    }

    private static readonly JsonSerializerOptions JsonOpts =
        new() { WriteIndented = false, PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
}
