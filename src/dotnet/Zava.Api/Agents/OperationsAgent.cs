using System.ComponentModel;
using System.Text.Json;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Zava.Api.Data;
using Zava.Api.Inference;

namespace Zava.Api.Agents;

/// <summary>
/// Operations agent: supply chain, inventory management, and supplier document parsing.
///
/// Tools: get_inventory, parse_supplier_doc, restock_suggestion.
/// </summary>
public sealed class OperationsAgent : ZavaAgentBase
{
    public override string Key => "operations";
    public override string Name => "Operations";
    public override string Description =>
        "Handles supply chain and inventory management: stock levels, supplier document parsing, and restock recommendations.";

    protected override AIAgent Agent { get; }

    private readonly ZavaDataStore _data;

    private const string SystemPrompt = """
        You are the Zava Operations Analyst — an expert in supply chain and inventory management.
        Help operations teams with:
        - Checking current inventory levels and stock health
        - Parsing and summarising supplier purchase orders and invoices
        - Identifying restock needs and priority items
        - Cross-referencing orders against inventory

        Use your tools to retrieve real-time data. Be precise with quantities and dates.
        Flag critical stock issues proactively.
        """;

    public OperationsAgent(IInferenceFactory inference, ZavaDataStore data)
    {
        _data = data;
        Agent = inference.CreateAgent(
            name: Name,
            description: Description,
            instructions: SystemPrompt,
            tools:
            [
                AIFunctionFactory.Create(GetInventoryAsync),
                AIFunctionFactory.Create(ParseSupplierDocAsync),
                AIFunctionFactory.Create(RestockSuggestionAsync),
            ]);
    }

    // ── Tools ─────────────────────────────────────────────────────────────────

    [Description("Get current inventory levels for one product or the entire catalog.")]
    private Task<string> GetInventoryAsync(
        [Description("Product ID to check (e.g. ZAVA-RUN-001); omit for full inventory summary")] string? productId = null)
    {
        if (productId is not null)
        {
            var product = _data.GetProduct(productId);
            if (product is null)
            {
                return Task.FromResult($"Product '{productId}' not found.");
            }

            return Task.FromResult(JsonSerializer.Serialize(new
            {
                productId = product.Id,
                name = product.Name,
                inStock = product.InStock,
                status = StockStatus(product.InStock),
                _source = "data/products.json",
            }, JsonOpts));
        }

        // Full catalog inventory
        var inventory = _data.Products.Select(p => new
        {
            productId = p.Id,
            name = p.Name,
            category = p.Category,
            inStock = p.InStock,
            status = StockStatus(p.InStock),
        }).OrderBy(p => p.inStock);

        return Task.FromResult(JsonSerializer.Serialize(new
        {
            totalSKUs = _data.Products.Count,
            inventory,
            _source = "data/products.json",
        }, JsonOpts));
    }

    private static string StockStatus(int qty) => qty switch
    {
        0 => "OUT_OF_STOCK",
        <= 50 => "CRITICAL",
        <= 100 => "LOW",
        <= 200 => "ADEQUATE",
        _ => "HEALTHY",
    };

    [Description("Parse and summarise a Zava supplier document (purchase order or invoice) by document name.")]
    private Task<string> ParseSupplierDocAsync(
        [Description("Supplier document name without extension (e.g. 'po-northfabric-2026-05', 'invoice-sporttex-q2')")] string docName)
    {
        var content = _data.GetSupplierDoc(docName);
        if (content is null)
        {
            var available = string.Join(", ", _data.SupplierDocNames);
            return Task.FromResult(
                $"Document '{docName}' not found. Available docs: {(string.IsNullOrEmpty(available) ? "none" : available)}");
        }

        // In Azure mode this would call Document Intelligence; locally we return raw content
        return Task.FromResult(JsonSerializer.Serialize(new
        {
            documentName = docName,
            parsedContent = content,
            note = "In Azure mode this is parsed by Azure Document Intelligence for structured extraction.",
            _source = $"suppliers/{docName}.md",
        }, JsonOpts));
    }

    [Description("Generate restock recommendations based on current inventory levels and recent order demand.")]
    private Task<string> RestockSuggestionAsync()
    {
        var orders = _data.Orders;
        // Count demand per product from recent orders
        var demand = orders
            .Where(o => o.Status is "Delivered" or "Shipped" or "Processing")
            .SelectMany(o => o.Items)
            .GroupBy(i => i.ProductId)
            .ToDictionary(g => g.Key, g => g.Sum(i => i.Qty));

        var suggestions = _data.Products
            .Where(p => p.InStock < 150)
            .Select(p =>
            {
                demand.TryGetValue(p.Id, out var recentDemand);
                var suggestQty = Math.Max(200 - p.InStock, recentDemand * 2);
                return new
                {
                    productId = p.Id,
                    name = p.Name,
                    currentStock = p.InStock,
                    status = StockStatus(p.InStock),
                    recentOrderDemand = recentDemand,
                    suggestedRestockQty = suggestQty,
                    priority = p.InStock < 100 ? "HIGH" : "MEDIUM",
                };
            })
            .OrderBy(s => s.currentStock)
            .ToList();

        return Task.FromResult(JsonSerializer.Serialize(new
        {
            generatedAt = DateTime.UtcNow.ToString("O"),
            restockItems = suggestions,
            _source = "data/products.json",
        }, JsonOpts));
    }

    private static readonly JsonSerializerOptions JsonOpts =
        new() { WriteIndented = false, PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
}
