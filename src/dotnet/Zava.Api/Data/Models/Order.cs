// Zava order (matches data/orders.json)
namespace Zava.Api.Data.Models;

public sealed class Order
{
    public string OrderId { get; set; } = string.Empty;
    public string Customer { get; set; } = string.Empty;
    public string CustomerName { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string PlacedOn { get; set; } = string.Empty;
    public List<OrderItem> Items { get; set; } = [];
    public decimal Total { get; set; }
    public string ShipTo { get; set; } = string.Empty;
}

public sealed class OrderItem
{
    public string ProductId { get; set; } = string.Empty;
    public int Qty { get; set; }
    public string Size { get; set; } = string.Empty;
    public string Color { get; set; } = string.Empty;
}
