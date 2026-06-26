using Azure.AI.OpenAI;
using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using Microsoft.Extensions.AI;
using OpenAI;
using OpenAI.Chat;
using OpenAI.Embeddings;

namespace Zava.Api.Inference;

/// <summary>
/// Builds <see cref="AIAgent"/> instances and embedding generators from configuration.
///
/// Provider selection (env var <c>INFERENCE_PROVIDER</c>):
///   github        — OpenAI client pointed at GitHub Models endpoint + GITHUB_TOKEN.
///   azure-openai  — Azure OpenAI via DefaultAzureCredential (no keys).
///   foundry       — Azure AI Foundry AIProjectClient via DefaultAzureCredential.
///
/// Same logic for <c>EMBEDDINGS_PROVIDER</c>.
/// Default = "github" so labs run without any Azure subscription.
/// </summary>
public sealed class InferenceFactory : IInferenceFactory
{
    private readonly IConfiguration _config;
    private readonly ILogger<InferenceFactory> _logger;

    public string InferenceProvider { get; }
    public string EmbeddingsProvider { get; }

    public InferenceFactory(IConfiguration config, ILogger<InferenceFactory> logger)
    {
        _config = config;
        _logger = logger;
        InferenceProvider = (config["INFERENCE_PROVIDER"] ?? "github").ToLowerInvariant();
        EmbeddingsProvider = (config["EMBEDDINGS_PROVIDER"] ?? "github").ToLowerInvariant();
        _logger.LogInformation(
            "Inference provider: {Chat}, Embeddings provider: {Emb}",
            InferenceProvider, EmbeddingsProvider);
    }

    // ── Chat agents ───────────────────────────────────────────────────────────

    public AIAgent CreateAgent(
        string name,
        string description,
        string instructions,
        IList<AITool>? tools = null)
    {
        _logger.LogDebug("Creating agent '{Name}' using provider '{Provider}'", name, InferenceProvider);
        return InferenceProvider switch
        {
            "foundry" => CreateFoundryAgent(name, description, instructions, tools),
            "azure-openai" => CreateAzureOpenAIAgent(name, description, instructions, tools),
            _ => CreateGitHubModelsAgent(name, description, instructions, tools),
        };
    }

    // ── Embeddings ────────────────────────────────────────────────────────────

    public IEmbeddingGenerator<string, Embedding<float>> CreateEmbeddingGenerator()
    {
        _logger.LogDebug("Creating embedding generator using provider '{Provider}'", EmbeddingsProvider);
        return EmbeddingsProvider switch
        {
            "foundry" => CreateFoundryEmbeddingGenerator(),
            "azure-openai" => CreateAzureOpenAIEmbeddingGenerator(),
            _ => CreateGitHubEmbeddingGenerator(),
        };
    }

    // ── GitHub Models (default, free — OpenAI-compatible endpoint) ───────────

    private AIAgent CreateGitHubModelsAgent(
        string name, string description, string instructions, IList<AITool>? tools)
    {
        var (client, model) = BuildGitHubOpenAIClient();
        // GetChatClient → AsIChatClient() bridges OpenAI SDK to Microsoft.Extensions.AI IChatClient
        IChatClient chatClient = client.GetChatClient(model).AsIChatClient();
        return chatClient.AsAIAgent(
            instructions: instructions,
            name: name,
            description: description,
            tools: tools ?? []);
    }

    private IEmbeddingGenerator<string, Embedding<float>> CreateGitHubEmbeddingGenerator()
    {
        var token = RequireEnv("GITHUB_TOKEN");
        var endpoint = _config["GITHUB_MODELS_ENDPOINT"] ?? "https://models.github.ai/inference";
        var model = _config["GITHUB_MODELS_EMBEDDING_MODEL"] ?? "openai/text-embedding-3-small";

        var clientOptions = new OpenAIClientOptions { Endpoint = new Uri(endpoint) };
        var client = new OpenAIClient(new System.ClientModel.ApiKeyCredential(token), clientOptions);
        // GetEmbeddingClient → AsIEmbeddingGenerator() bridges to IEmbeddingGenerator
        return client.GetEmbeddingClient(model).AsIEmbeddingGenerator();
    }

    private (OpenAIClient client, string model) BuildGitHubOpenAIClient()
    {
        var token = RequireEnv("GITHUB_TOKEN");
        var endpoint = _config["GITHUB_MODELS_ENDPOINT"] ?? "https://models.github.ai/inference";
        var model = _config["GITHUB_MODELS_CHAT_MODEL"] ?? "openai/gpt-4o-mini";

        var clientOptions = new OpenAIClientOptions { Endpoint = new Uri(endpoint) };
        return (new OpenAIClient(new System.ClientModel.ApiKeyCredential(token), clientOptions), model);
    }

    // ── Azure OpenAI (DefaultAzureCredential — no API keys) ──────────────────

    private AIAgent CreateAzureOpenAIAgent(
        string name, string description, string instructions, IList<AITool>? tools)
    {
        var endpoint = RequireEnv("AZURE_OPENAI_ENDPOINT");
        var deployment = _config["AZURE_OPENAI_CHAT_DEPLOYMENT"] ?? "gpt-4o-mini";

        // AzureOpenAIClient uses DefaultAzureCredential — no API keys required.
        IChatClient chatClient = BuildAzureOpenAIClient(endpoint).GetChatClient(deployment).AsIChatClient();
        return chatClient.AsAIAgent(
            instructions: instructions,
            name: name,
            description: description,
            tools: tools ?? []);
    }

    private IEmbeddingGenerator<string, Embedding<float>> CreateAzureOpenAIEmbeddingGenerator()
    {
        var endpoint = RequireEnv("AZURE_OPENAI_ENDPOINT");
        var deployment = _config["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] ?? "text-embedding-3-small";
        return BuildAzureOpenAIClient(endpoint).GetEmbeddingClient(deployment).AsIEmbeddingGenerator();
    }

    private static AzureOpenAIClient BuildAzureOpenAIClient(string endpoint) =>
        new(new Uri(endpoint), new DefaultAzureCredential());

    // ── Azure AI Foundry (preferred Azure path) ───────────────────────────────

    private AIAgent CreateFoundryAgent(
        string name, string description, string instructions, IList<AITool>? tools)
    {
        var projectEndpoint = RequireEnv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT");
        var deployment = _config["AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT"] ?? "gpt-4o-mini";

        // Microsoft.Agents.AI.Foundry adds AsAIAgent() on AIProjectClient.
        return new AIProjectClient(new Uri(projectEndpoint), new DefaultAzureCredential())
            .AsAIAgent(
                model: deployment,
                instructions: instructions,
                name: name,
                description: description,
                tools: tools ?? []);
    }

    private IEmbeddingGenerator<string, Embedding<float>> CreateFoundryEmbeddingGenerator()
    {
        // Foundry projects expose an Azure OpenAI-compatible resource endpoint for embeddings.
        // Use AZURE_AI_FOUNDRY_RESOURCE_ENDPOINT (base, without /api/projects/...) if set,
        // otherwise strip the project path from AZURE_AI_FOUNDRY_PROJECT_ENDPOINT.
        var projectEndpoint = RequireEnv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT");
        var resourceEndpoint = _config["AZURE_AI_FOUNDRY_RESOURCE_ENDPOINT"]
                               ?? StripProjectPath(projectEndpoint);
        var deployment = _config["AZURE_AI_FOUNDRY_EMBEDDING_DEPLOYMENT"] ?? "text-embedding-3-small";

        return BuildAzureOpenAIClient(resourceEndpoint).GetEmbeddingClient(deployment).AsIEmbeddingGenerator();
    }

    // Strip /api/projects/<name> from a Foundry project endpoint to get the resource base URL
    private static string StripProjectPath(string projectEndpoint)
    {
        var idx = projectEndpoint.IndexOf("/api/projects", StringComparison.OrdinalIgnoreCase);
        return idx > 0 ? projectEndpoint[..idx] : projectEndpoint;
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private string RequireEnv(string key) =>
        _config[key]
        ?? throw new InvalidOperationException(
            $"Required configuration '{key}' is not set. "
            + $"Check your .env file or environment variables.");
}
