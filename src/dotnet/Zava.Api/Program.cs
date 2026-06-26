using System.Diagnostics;
using System.Text.Json;
using Azure.Monitor.OpenTelemetry.AspNetCore;
using Microsoft.Extensions.AI;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using Zava.Api.Agents;
using Zava.Api.Data;
using Zava.Api.Inference;
using ZavaChatRequest = Zava.Api.Models.ChatRequest;
using ZavaChatResponse = Zava.Api.Models.ChatResponse;

// ── Load .env file (dev mode; ignored if not present) ─────────────────────────
LoadDotEnv();

var builder = WebApplication.CreateBuilder(args);

// ── Configuration ──────────────────────────────────────────────────────────────
builder.Configuration
    .AddEnvironmentVariables()
    .AddJsonFile("appsettings.json", optional: false)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true);

// ── OpenTelemetry ──────────────────────────────────────────────────────────────
var appInsightsConnString = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];

var otelBuilder = builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("zava-api-dotnet"))
    .WithTracing(tracing =>
    {
        tracing
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation();
    });

if (!string.IsNullOrEmpty(appInsightsConnString))
{
    // Export to Azure Monitor / Application Insights when connection string is set
    otelBuilder.UseAzureMonitor();
}

// ── Core services ──────────────────────────────────────────────────────────────
builder.Services.AddSingleton<IInferenceFactory, InferenceFactory>();
builder.Services.AddSingleton<ZavaDataStore>();
builder.Services.AddTransient<ZavaSeeder>();

// Singleton embedding generator (reused across requests)
builder.Services.AddSingleton<IEmbeddingGenerator<string, Embedding<float>>>(sp =>
    sp.GetRequiredService<IInferenceFactory>().CreateEmbeddingGenerator());

// ── Agents (singletons — each wraps an AIAgent with its own session cache) ─────
// Registered as IEnumerable<ZavaAgentBase> so AgentRegistry can be composed in tests.
builder.Services.AddSingleton<ZavaAgentBase, ConciergeAgent>();
builder.Services.AddSingleton<ZavaAgentBase, MerchandiserAgent>();
builder.Services.AddSingleton<ZavaAgentBase, OperationsAgent>();
builder.Services.AddSingleton<ZavaAgentBase, TrustAgent>();
builder.Services.AddSingleton<ZavaAgentBase, OrchestratorAgent>();
builder.Services.AddSingleton<AgentRegistry>();

// ── CORS (lenient for lab/demo use) ───────────────────────────────────────────
builder.Services.AddCors(opts => opts.AddDefaultPolicy(policy =>
    policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();

// ── Middleware ─────────────────────────────────────────────────────────────────
app.UseCors();

// ── Startup seeding (background, non-blocking) ────────────────────────────────
_ = Task.Run(async () =>
{
    using var scope = app.Services.CreateScope();
    var seeder = scope.ServiceProvider.GetRequiredService<ZavaSeeder>();
    try
    {
        await seeder.SeedAsync();
    }
    catch (Exception ex)
    {
        var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "Seed error (non-fatal) — app will start with partial data");
    }
});

// ── Routes ─────────────────────────────────────────────────────────────────────

// GET /health  →  {"status":"ok"}
app.MapGet("/health", () => Results.Ok(new { status = "ok" }))
    .WithName("Health")
    .WithDescription("Health check endpoint");

// GET /agents  →  [{key, name, description}]
app.MapGet("/agents", (AgentRegistry registry) => Results.Ok(registry.GetAgentInfos()))
    .WithName("ListAgents")
    .WithDescription("Returns metadata for all registered Zava agents");

// POST /chat  →  {reply, agent, citations, traceId}
app.MapPost("/chat", async (ZavaChatRequest req, AgentRegistry registry, CancellationToken ct) =>
{
    if (string.IsNullOrWhiteSpace(req.Message))
    {
        return Results.BadRequest(new { error = "message is required" });
    }

    var agent = registry.Resolve(req.Agent);
    var result = await agent.RunAsync(req.Message, req.SessionId, ct);

    var traceId = Activity.Current?.TraceId.ToString() ?? result.TraceId;
    return Results.Ok(new ZavaChatResponse
    {
        Reply = result.Reply,
        Agent = agent.Key,
        Citations = result.Citations,
        TraceId = traceId,
    });
})
.WithName("Chat")
.WithDescription("Non-streaming chat: routes to the specified agent (defaults to orchestrator)");

// POST /chat/stream  →  SSE token stream
app.MapPost("/chat/stream", async (HttpContext ctx, ZavaChatRequest req, AgentRegistry registry) =>
{
    if (string.IsNullOrWhiteSpace(req.Message))
    {
        ctx.Response.StatusCode = 400;
        return;
    }

    ctx.Response.Headers["Content-Type"] = "text/event-stream";
    ctx.Response.Headers["Cache-Control"] = "no-cache";
    ctx.Response.Headers["Connection"] = "keep-alive";

    var agent = registry.Resolve(req.Agent);
    var ct = ctx.RequestAborted;
    var traceId = Activity.Current?.TraceId.ToString() ?? string.Empty;

    await ctx.Response.WriteAsync(
        $"data: {JsonSerializer.Serialize(new { @event = "start", agent = agent.Key, traceId })}\n\n", ct);

    await foreach (var chunk in agent.RunStreamingAsync(req.Message, req.SessionId, ct))
    {
        var json = JsonSerializer.Serialize(new { @event = "token", text = chunk });
        await ctx.Response.WriteAsync($"data: {json}\n\n", ct);
        await ctx.Response.Body.FlushAsync(ct);
    }

    await ctx.Response.WriteAsync(
        $"data: {JsonSerializer.Serialize(new { @event = "end" })}\n\n", ct);
})
.WithName("ChatStream")
.WithDescription("SSE streaming chat: emits token events as agent generates the reply");

app.Run();

// ── Helpers ────────────────────────────────────────────────────────────────────

/// Walks up the directory tree from cwd looking for a .env file and loads it.
/// DotNetEnv 3.x removed the TraversalLoad method; we replicate the behaviour here.
static void LoadDotEnv()
{
    var dir = Directory.GetCurrentDirectory();
    while (!string.IsNullOrEmpty(dir))
    {
        var candidate = Path.Combine(dir, ".env");
        if (File.Exists(candidate))
        {
            DotNetEnv.Env.Load(candidate);
            return;
        }
        var parent = Path.GetDirectoryName(dir);
        if (parent == dir)
        {
            break;
        }

        dir = parent!;
    }
}

// Make Program accessible to integration tests
public partial class Program { }

