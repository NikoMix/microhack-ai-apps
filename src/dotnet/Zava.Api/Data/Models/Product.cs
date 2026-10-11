// Zava smart-apparel catalog item (matches data/products.json)
namespace Zava.Api.Data.Models;

public sealed class Product
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string Subcategory { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public string Currency { get; set; } = "USD";
    public List<string> Sizes { get; set; } = [];
    public List<string> Colors { get; set; } = [];
    public List<string> SmartFeatures { get; set; } = [];
    public int BatteryHours { get; set; }
    public int WashCycles { get; set; }
    public string Description { get; set; } = string.Empty;
    public int InStock { get; set; }
    public double Rating { get; set; }
}
