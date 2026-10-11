// Product review (matches data/reviews.json)
namespace Zava.Api.Data.Models;

public sealed class Review
{
    public string ProductId { get; set; } = string.Empty;
    public string Customer { get; set; } = string.Empty;
    public int Rating { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Text { get; set; } = string.Empty;
}
