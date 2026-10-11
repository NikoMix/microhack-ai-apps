using FluentAssertions;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging.Abstractions;
using Zava.Api.Inference;

namespace Zava.Tests;

/// <summary>
/// Tests for <see cref="InferenceFactory"/> — verifies provider-switch logic.
/// Each test supplies environment configuration directly; no real network calls are made.
/// </summary>
public sealed class InferenceFactoryTests
{
    // ── Factory construction ─────────────────────────────────────────────────

    [Fact]
    public void Constructor_DefaultsToGitHubProvider()
    {
        var factory = BuildFactory();
        factory.InferenceProvider.Should().Be("github");
        factory.EmbeddingsProvider.Should().Be("github");
    }

    [Theory]
    [InlineData("github")]
    [InlineData("azure-openai")]
    [InlineData("foundry")]
    public void Constructor_ReadsInferenceProviderFromConfig(string provider)
    {
        var factory = BuildFactory(chat: provider, emb: provider);
        factory.InferenceProvider.Should().Be(provider);
        factory.EmbeddingsProvider.Should().Be(provider);
    }

    [Theory]
    [InlineData("UNKNOWN")]
    [InlineData("")]
    [InlineData("GITHUB")] // case mismatch
    public void Constructor_NormalisesProviderToLowerCase(string input)
    {
        var factory = BuildFactory(chat: input);
        factory.InferenceProvider.Should().Be(input.ToLowerInvariant());
    }

    // ── GitHub provider — fails fast on missing token ─────────────────────

    [Fact]
    public void CreateAgent_GitHub_ThrowsWhenTokenMissing()
    {
        var factory = BuildFactory(chat: "github"); // no GITHUB_TOKEN configured
        var act = () => factory.CreateAgent("test", "desc", "instructions");
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*GITHUB_TOKEN*");
    }

    [Fact]
    public void CreateEmbeddingGenerator_GitHub_ThrowsWhenTokenMissing()
    {
        var factory = BuildFactory(emb: "github");
        var act = () => factory.CreateEmbeddingGenerator();
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*GITHUB_TOKEN*");
    }

    // ── Azure OpenAI provider — fails fast on missing endpoint ───────────

    [Fact]
    public void CreateAgent_AzureOpenAI_ThrowsWhenEndpointMissing()
    {
        var factory = BuildFactory(chat: "azure-openai"); // no AZURE_OPENAI_ENDPOINT
        var act = () => factory.CreateAgent("test", "desc", "instructions");
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*AZURE_OPENAI_ENDPOINT*");
    }

    [Fact]
    public void CreateEmbeddingGenerator_AzureOpenAI_ThrowsWhenEndpointMissing()
    {
        var factory = BuildFactory(emb: "azure-openai");
        var act = () => factory.CreateEmbeddingGenerator();
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*AZURE_OPENAI_ENDPOINT*");
    }

    // ── Foundry provider — fails fast on missing endpoint ────────────────

    [Fact]
    public void CreateAgent_Foundry_ThrowsWhenEndpointMissing()
    {
        var factory = BuildFactory(chat: "foundry");
        var act = () => factory.CreateAgent("test", "desc", "instructions");
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*AZURE_AI_FOUNDRY_PROJECT_ENDPOINT*");
    }

    [Fact]
    public void CreateEmbeddingGenerator_Foundry_ThrowsWhenEndpointMissing()
    {
        var factory = BuildFactory(emb: "foundry");
        var act = () => factory.CreateEmbeddingGenerator();
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*AZURE_AI_FOUNDRY*");
    }

    // ── GitHub with token — succeeds object construction ─────────────────

    [Fact]
    public void CreateEmbeddingGenerator_GitHub_WithToken_ReturnsGenerator()
    {
        var factory = BuildFactory(
            emb: "github",
            extra: new Dictionary<string, string?> { ["GITHUB_TOKEN"] = "fake-token" });

        // Object construction should succeed; actual API calls would fail at runtime
        var gen = factory.CreateEmbeddingGenerator();
        gen.Should().NotBeNull();
        gen.Should().BeAssignableTo<IEmbeddingGenerator<string, Embedding<float>>>();
    }

    // ── Helpers ───────────────────────────────────────────────────────────

    private static InferenceFactory BuildFactory(
        string? chat = null,
        string? emb = null,
        Dictionary<string, string?>? extra = null)
    {
        var dict = new Dictionary<string, string?>();
        if (chat is not null)
        {
            dict["INFERENCE_PROVIDER"] = chat;
        }

        if (emb is not null)
        {
            dict["EMBEDDINGS_PROVIDER"] = emb;
        }

        if (extra is not null)
        {
            foreach (var (k, v) in extra)
            {
                dict[k] = v;
            }
        }

        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(dict)
            .Build();

        return new InferenceFactory(config, NullLogger<InferenceFactory>.Instance);
    }
}
