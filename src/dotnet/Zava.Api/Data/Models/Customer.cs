// Zava business unit (matches data/customers.json — B.2.2 diversity)
namespace Zava.Api.Data.Models;

public sealed class Customer
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string Industry { get; set; } = string.Empty;
    public string AssociationType { get; set; } = string.Empty;
    public List<string> PrimaryPillars { get; set; } = [];
    public string Description { get; set; } = string.Empty;
}
