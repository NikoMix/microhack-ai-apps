using System.Net;
using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text.Json;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Zava.Api.Agents;
using Zava.Api.Inference;

namespace Zava.Tests;

/// <summary>
/// Integration tests for the Zava HTTP API.
///
/// Uses <see cref="WebApplicationFactory{TEntryPoint}"/> with stub agents so
/// no LLM or Azure connections are needed — tests run fully in-process.
/// </summary>
public sealed class ApiTests : IClassFixture<ApiTests.ZavaWebFactory>
{
    private readonly HttpClient _client;

    public ApiTests(ZavaWebFactory factory)
    {
        _client = factory.CreateClient();
    }

    // ── GET /health ───────────────────────────────────────────────────────────

    [Fact]
    public async Task GetHealth_Returns200WithOkStatus()
    {
        var response = await _client.GetAsync("/health");
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var json = await response.Content.ReadFromJsonAsync<JsonElement>();
        json.GetProperty("status").GetString().Should().Be("ok");
    }

    // ── GET /agents ───────────────────────────────────────────────────────────

    [Fact]
    public async Task GetAgents_Returns200WithFiveAgents()
    {
        var response = await _client.GetAsync("/agents");
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var agents = await response.Content.ReadFromJsonAsync<JsonElement[]>();
        agents.Should().NotBeNullOrEmpty();
        agents!.Length.Should().Be(5);
    }

    [Fact]
    public async Task GetAgents_EachAgentHasRequiredFields()
    {
        var response = await _client.GetAsync("/agents");
        var agents = await response.Content.ReadFromJsonAsync<JsonElement[]>();

        foreach (var agent in agents!)
        {
            agent.TryGetProperty("key", out _).Should().BeTrue("each agent should have 'key'");
            agent.TryGetProperty("name", out _).Should().BeTrue("each agent should have 'name'");
            agent.TryGetProperty("description", out _).Should().BeTrue("each agent should have 'description'");
        }
    }

    [Fact]
    public async Task GetAgents_ContainsAllExpectedKeys()
    {
        var response = await _client.GetAsync("/agents");
        var agents = await response.Content.ReadFromJsonAsync<JsonElement[]>();
        var keys = agents!.Select(a => a.GetProperty("key").GetString()).ToHashSet();

        keys.Should().Contain("concierge");
        keys.Should().Contain("merchandiser");
        keys.Should().Contain("operations");
        keys.Should().Contain("trust");
        keys.Should().Contain("orchestrator");
    }

    // ── POST /chat ─────────────────────────────────────────────────────────────

    [Fact]
    public async Task PostChat_EmptyMessage_Returns400()
    {
        var response = await _client.PostAsJsonAsync("/chat", new { message = "" });
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task PostChat_ValidMessage_Returns200WithRequiredFields()
    {
        var response = await _client.PostAsJsonAsync("/chat",
            new { message = "Hello", agent = "concierge" });

        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var json = await response.Content.ReadFromJsonAsync<JsonElement>();
        json.TryGetProperty("reply", out _).Should().BeTrue("response should contain 'reply'");
        json.TryGetProperty("agent", out _).Should().BeTrue("response should contain 'agent'");
        json.TryGetProperty("citations", out _).Should().BeTrue("response should contain 'citations'");
        json.TryGetProperty("traceId", out _).Should().BeTrue("response should contain 'traceId'");
    }

    [Fact]
    public async Task PostChat_NoAgentSpecified_UsesOrchestrator()
    {
        var response = await _client.PostAsJsonAsync("/chat",
            new { message = "What products do you have?" });

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var json = await response.Content.ReadFromJsonAsync<JsonElement>();
        json.GetProperty("agent").GetString().Should().Be("orchestrator");
    }

    [Fact]
    public async Task PostChat_SpecifiedAgent_ReturnsCorrectAgentKey()
    {
        var response = await _client.PostAsJsonAsync("/chat",
            new { message = "Search for running gear", agent = "merchandiser" });

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var json = await response.Content.ReadFromJsonAsync<JsonElement>();
        json.GetProperty("agent").GetString().Should().Be("merchandiser");
    }

    // ── POST /chat/stream ──────────────────────────────────────────────────────

    [Fact]
    public async Task PostChatStream_EmptyMessage_Returns400()
    {
        var response = await _client.PostAsJsonAsync("/chat/stream", new { message = "" });
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task PostChatStream_ValidMessage_ReturnsSseContentType()
    {
        var response = await _client.PostAsJsonAsync("/chat/stream",
            new { message = "Tell me about products", agent = "concierge" });

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var ct = response.Content.Headers.ContentType?.MediaType;
        ct.Should().Be("text/event-stream");
    }

    // ── Test infrastructure ───────────────────────────────────────────────────

    /// <summary>
    /// Custom WebApplicationFactory that replaces all agents with fast stubs
    /// so no LLM calls, no tokens, and no Azure credentials are needed.
    /// </summary>
    public sealed class ZavaWebFactory : WebApplicationFactory<Program>
    {
        protected override void ConfigureWebHost(Microsoft.AspNetCore.Hosting.IWebHostBuilder builder)
        {
            // Suppress the background seeder (it will fail gracefully without a real DATA_PATH).
            // Set a token so startup validation passes.
            builder.UseSetting("GITHUB_TOKEN", "test-stub-token");

            builder.ConfigureServices(services =>
            {
                // Remove all real agent registrations and the real inference factory
                services.RemoveAll<ZavaAgentBase>();
                var inferenceDescriptor = services.FirstOrDefault(d => d.ServiceType == typeof(IInferenceFactory));
                if (inferenceDescriptor is not null)
                {
                    services.Remove(inferenceDescriptor);
                }

                var embeddingDescriptor = services.FirstOrDefault(
                    d => d.ServiceType == typeof(Microsoft.Extensions.AI.IEmbeddingGenerator<string, Microsoft.Extensions.AI.Embedding<float>>));
                if (embeddingDescriptor is not null)
                {
                    services.Remove(embeddingDescriptor);
                }

                // Register stub inference factory
                services.AddSingleton<IInferenceFactory, StubInferenceFactory>();

                // Register stub embedding generator
                services.AddSingleton<Microsoft.Extensions.AI.IEmbeddingGenerator<string, Microsoft.Extensions.AI.Embedding<float>>>(
                    _ => new StubEmbeddingGenerator());

                // Register 5 stub agents as ZavaAgentBase
                services.AddSingleton<ZavaAgentBase>(new StubAgent("concierge", "Concierge", "Zava virtual concierge"));
                services.AddSingleton<ZavaAgentBase>(new StubAgent("merchandiser", "Merchandiser", "Zava product expert"));
                services.AddSingleton<ZavaAgentBase>(new StubAgent("operations", "Operations", "Zava logistics agent"));
                services.AddSingleton<ZavaAgentBase>(new StubAgent("trust", "Trust", "Zava compliance agent"));
                services.AddSingleton<ZavaAgentBase>(new StubAgent("orchestrator", "Orchestrator", "Zava triage agent"));
            });
        }
    }

    // ── Stub agent ────────────────────────────────────────────────────────────

    /// <summary>
    /// Test double for any ZavaAgentBase subclass.
    /// Overrides RunAsync / RunStreamingAsync to return canned responses.
    /// Never accesses the inference provider — no tokens needed.
    /// </summary>
    private sealed class StubAgent : ZavaAgentBase
    {
        public override string Key { get; }
        public override string Name { get; }
        public override string Description { get; }

        // Agent is never accessed — overrides bypass it entirely.
        protected override Microsoft.Agents.AI.AIAgent Agent =>
            throw new NotSupportedException("Stub agent does not use AIAgent.");

        public StubAgent(string key, string name, string description)
        {
            Key = key;
            Name = name;
            Description = description;
        }

        public override Task<AgentRunResult> RunAsync(
            string message,
            string? sessionId = null,
            CancellationToken ct = default) =>
            Task.FromResult(new AgentRunResult
            {
                Reply = $"[Stub] {Key} received: {message}",
                Citations = [],
                TraceId = string.Empty,
            });

        public override async IAsyncEnumerable<string> RunStreamingAsync(
            string message,
            string? sessionId = null,
            [EnumeratorCancellation] CancellationToken ct = default)
        {
            await Task.CompletedTask;
            yield return $"[Stub] {Key}: ";
            yield return message;
        }
    }

    // ── Stub inference factory (never actually called since agents are stubbed) ──

    private sealed class StubInferenceFactory : IInferenceFactory
    {
        public string InferenceProvider => "stub";
        public string EmbeddingsProvider => "stub";

        public Microsoft.Agents.AI.AIAgent CreateAgent(
            string name,
            string description,
            string instructions,
            System.Collections.Generic.IList<Microsoft.Extensions.AI.AITool>? tools = null) =>
            throw new NotSupportedException("StubInferenceFactory.CreateAgent should not be called in tests.");

        public Microsoft.Extensions.AI.IEmbeddingGenerator<string, Microsoft.Extensions.AI.Embedding<float>> CreateEmbeddingGenerator() =>
            new StubEmbeddingGenerator();
    }

    // ── Stub embedding generator (returns zero vectors) ────────────────────────

    private sealed class StubEmbeddingGenerator
        : Microsoft.Extensions.AI.IEmbeddingGenerator<string, Microsoft.Extensions.AI.Embedding<float>>
    {
        public Microsoft.Extensions.AI.EmbeddingGeneratorMetadata Metadata { get; } =
            new Microsoft.Extensions.AI.EmbeddingGeneratorMetadata("stub");

        public Task<Microsoft.Extensions.AI.GeneratedEmbeddings<Microsoft.Extensions.AI.Embedding<float>>> GenerateAsync(
            System.Collections.Generic.IEnumerable<string> values,
            Microsoft.Extensions.AI.EmbeddingGenerationOptions? options = null,
            CancellationToken cancellationToken = default)
        {
            var result = new Microsoft.Extensions.AI.GeneratedEmbeddings<Microsoft.Extensions.AI.Embedding<float>>(
                values.Select(_ => new Microsoft.Extensions.AI.Embedding<float>(new float[1536])).ToList());
            return Task.FromResult(result);
        }

        public object? GetService(Type serviceType, object? serviceKey = null) => null;
        public void Dispose() { }
    }
}
