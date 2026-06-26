using System.ComponentModel;
using System.Text.Json;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Zava.Api.Data;
using Zava.Api.Inference;

namespace Zava.Api.Agents;

/// <summary>
/// Trust agent: content safety, governance, and audit-evidence generation.
///
/// Tools: content_safety_check, policy_lookup, generate_evidence.
/// This agent is central to Module B controls B.1.1–B.4.2.
/// </summary>
public sealed class TrustAgent : ZavaAgentBase
{
    public override string Key => "trust";
    public override string Name => "Trust &amp; Compliance";
    public override string Description =>
        "Checks content safety, looks up compliance policies, and generates Module B audit evidence for the AI Applications on Microsoft Azure Advanced Specialization.";

    protected override AIAgent Agent { get; }

    private readonly ZavaDataStore _data;

    private const string SystemPrompt = """
        You are the Zava Trust & Compliance Officer — an AI governance specialist.
        Your responsibilities:
        - Evaluate content for safety, bias, and policy compliance
        - Look up Zava's internal policies and standards
        - Generate audit evidence packages for the Microsoft AI Applications
          Advanced Specialization (Module B controls B.1.1–B.4.2)
        - Advise on responsible AI practices

        When generating evidence, be thorough, accurate, and reference real artifacts
        from the Zava AI platform build. Include control IDs and coverage mappings.
        """;

    public TrustAgent(IInferenceFactory inference, ZavaDataStore data)
    {
        _data = data;
        Agent = inference.CreateAgent(
            name: Name,
            description: Description,
            instructions: SystemPrompt,
            tools:
            [
                AIFunctionFactory.Create(ContentSafetyCheckAsync),
                AIFunctionFactory.Create(PolicyLookupAsync),
                AIFunctionFactory.Create(GenerateEvidenceAsync),
            ]);
    }

    // ── Tools ─────────────────────────────────────────────────────────────────

    [Description("Check text content for safety issues: harmful content, PII exposure, bias, or policy violations.")]
    private Task<string> ContentSafetyCheckAsync(
        [Description("The text content to evaluate for safety and compliance")] string content)
    {
        // In Azure mode this calls Azure Content Safety; locally we apply heuristics.
        var (isHarmful, categories) = LocalSafetyCheck(content);

        return Task.FromResult(JsonSerializer.Serialize(new
        {
            content = content.Length > 100 ? content[..100] + "…" : content,
            isSafe = !isHarmful,
            categories = categories.Count > 0 ? categories : new List<string> { "none" },
            provider = "local-heuristic (use Azure Content Safety in production)",
            recommendation = isHarmful
                ? "Review and revise the content before publishing."
                : "Content appears safe to publish.",
            _source = "Azure Content Safety (azure-contentsafety.microsoft.com)",
        }, JsonOpts));
    }

    private static (bool harmful, List<string> categories) LocalSafetyCheck(string text)
    {
        var lower = text.ToLowerInvariant();
        var categories = new List<string>();

        // Very simple heuristic — in production use Azure Content Safety API
        string[] harmful = ["hate", "violence", "illegal", "harm", "abuse", "exploit"];
        foreach (var word in harmful)
        {
            if (lower.Contains(word, StringComparison.Ordinal))
            {
                categories.Add(word);
            }
        }
        return (categories.Count > 0, categories);
    }

    [Description("Look up a Zava policy by topic (e.g. returns, warranty, sustainability, smart-garment-care, sizing).")]
    private Task<string> PolicyLookupAsync(
        [Description("Policy topic to look up (e.g. 'returns', 'warranty', 'sustainability', 'sizing', 'smart-garment-care')")] string topic)
    {
        var docs = _data.SearchKnowledge(topic, topK: 2);
        if (docs.Count == 0)
        {
            return Task.FromResult($"No policy found for topic '{topic}'. Available topics: returns, warranty, sustainability, sizing, smart-garment-care.");
        }

        return Task.FromResult(JsonSerializer.Serialize(docs.Select(d => new
        {
            d.Title,
            d.Content,
            _source = d.Source,
        }), JsonOpts));
    }

    [Description("Generate Module B audit evidence package for the AI Applications on Microsoft Azure Advanced Specialization.")]
    private Task<string> GenerateEvidenceAsync(
        [Description("Optional control ID filter (e.g. 'B.1.1', 'B.4.1'); omit for full evidence package")] string? controlId = null)
    {
        var allControls = BuildModuleBEvidence();
        var controls = controlId is null
            ? allControls
            : allControls.Where(c => c.ControlId.StartsWith(controlId, StringComparison.OrdinalIgnoreCase)).ToList();

        var evidence = new
        {
            packageName = "Zava AI Agent Platform — Module B Evidence Package",
            generatedAt = DateTime.UtcNow.ToString("O"),
            organization = "Zava (Intelligent Athletic Apparel)",
            specialization = "AI Applications on Microsoft Azure",
            controls,
            summary = new
            {
                totalControls = controls.Count,
                covered = controls.Count(c => c.Status == "Covered"),
                partial = controls.Count(c => c.Status == "Partial"),
            },
            _source = "docs/module-b-mapping.md",
        };

        return Task.FromResult(JsonSerializer.Serialize(evidence, JsonOpts));
    }

    private static List<EvidenceControl> BuildModuleBEvidence() =>
    [
        new()
        {
            ControlId = "B.1.1",
            Title = "Azure AI Implementation",
            Status = "Covered",
            Artifacts =
            [
                "Architecture diagram: docs/architecture.md",
                "AI services used: Azure AI Foundry, Azure OpenAI, Azure AI Search, Document Intelligence, Content Safety",
                "Agents: concierge, merchandiser, operations, trust, orchestrator on Microsoft Agent Framework",
                "Capability statement: auto-generated by trust.generate_evidence",
            ],
            AzureServices = ["Azure AI Foundry", "Azure OpenAI", "Azure AI Search", "Azure Document Intelligence", "Azure Content Safety"],
        },
        new()
        {
            ControlId = "B.2.1",
            Title = "ACR Performance — Three Pillars",
            Status = "Covered",
            Artifacts =
            [
                "AI Services pillar: AI Foundry + OpenAI + Search + Doc Intelligence + Content Safety",
                "App Platform pillar: Azure Container Apps + ACR + API Management",
                "Data pillar: Cosmos DB (products/orders/customers) + PostgreSQL pgvector",
            ],
            AzureServices = ["Azure Container Apps", "Azure Container Registry", "Azure Cosmos DB", "Azure Database for PostgreSQL"],
        },
        new()
        {
            ControlId = "B.2.2",
            Title = "Customer Diversity",
            Status = "Covered",
            Artifacts =
            [
                "Zava Retail Stores — PAL association (physical retail, App Platform + Data)",
                "Zava eCommerce — DPOR association (D2C web/mobile, AI + App Platform + Data)",
                "Zava Wholesale — CSP association (B2B, Data + App Platform)",
                "Customer data: data/customers.json",
            ],
            AzureServices = [],
        },
        new()
        {
            ControlId = "B.3.1",
            Title = "Certifications",
            Status = "Covered",
            Artifacts =
            [
                "AZ-204: Azure Developer Associate — API, Container Apps, Cosmos DB labs",
                "AI-102: Azure AI Engineer — AI Foundry, Search, Safety labs",
                "DP-420: Azure Cosmos DB Developer — data modeling lab",
                "AZ-400: DevOps Engineer — CI/CD pipeline lab",
                "Crosswalk: docs/cert-crosswalk.md",
            ],
            AzureServices = [],
        },
        new()
        {
            ControlId = "B.4.1",
            Title = "Audit Readiness",
            Status = "Covered",
            Artifacts =
            [
                "Evidence package (this document)",
                "Pre-audit checklist: docs/evidence-templates/",
                "Architecture diagram + capability statement: auto-generated",
                "Security baseline: Managed Identity, Key Vault, no keys in code",
            ],
            AzureServices = ["Azure Key Vault"],
        },
        new()
        {
            ControlId = "B.4.2",
            Title = "Partner Onboarding",
            Status = "Covered",
            Artifacts =
            [
                "TTT facilitator guide: docs/facilitator-guide/",
                "Lab guides: docs/labs/",
                "Solution guides: docs/solutions/",
                "Delivery templates: docs/evidence-templates/",
            ],
            AzureServices = [],
        },
    ];

    private sealed class EvidenceControl
    {
        public string ControlId { get; init; } = string.Empty;
        public string Title { get; init; } = string.Empty;
        public string Status { get; init; } = string.Empty;
        public List<string> Artifacts { get; init; } = [];
        public List<string> AzureServices { get; init; } = [];
    }

    private static readonly JsonSerializerOptions JsonOpts =
        new() { WriteIndented = false, PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
}
