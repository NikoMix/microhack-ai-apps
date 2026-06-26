# Zava .NET Agent API

ASP.NET Core Minimal API implementing the Zava AI agent platform for the
**AI Applications on Microsoft Azure** MicroHack (Module B).

- Five agents: `concierge`, `merchandiser`, `operations`, `trust`, `orchestrator`
- Modular inference: **GitHub Models** (default/free), **Azure OpenAI**, **Azure AI Foundry**
- OpenTelemetry → Application Insights (optional)
- No API keys in code — `DefaultAzureCredential` for all Azure calls

---

## Prerequisites

| Tool | Version |
|------|---------|
| .NET SDK | 10.0+ |
| Docker | 24+ (for container build) |

---

## Quick start — GitHub Models mode (no Azure required)

```bash
# 1. Copy and populate the .env file
cp .env.sample .env
# Edit .env: set GITHUB_TOKEN=<your GitHub PAT with models:read scope>

# 2. Restore and run
cd src/dotnet
dotnet run --project Zava.Api
```

The API starts on <http://localhost:5000>.

**Verify:**
```bash
curl http://localhost:5000/health   # {"status":"ok"}
curl http://localhost:5000/agents   # [{key,name,description},...]
curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"What running gear do you have?","agent":"merchandiser"}'
```

### Environment variables (GitHub mode)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | ✅ | — | GitHub PAT with `models:read` scope |
| `INFERENCE_PROVIDER` | ❌ | `github` | `github` \| `azure-openai` \| `foundry` |
| `EMBEDDINGS_PROVIDER` | ❌ | `github` | `github` \| `azure-openai` \| `foundry` |
| `GITHUB_MODELS_ENDPOINT` | ❌ | `https://models.github.ai/inference` | Override endpoint |
| `GITHUB_MODELS_CHAT_MODEL` | ❌ | `openai/gpt-4o-mini` | Chat model name |
| `GITHUB_MODELS_EMBEDDING_MODEL` | ❌ | `openai/text-embedding-3-small` | Embedding model |
| `DATA_PATH` | ❌ | auto-detected | Path to `data/` directory |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | ❌ | — | Enables Azure Monitor export |

---

## Azure mode (Azure OpenAI)

```bash
# .env
INFERENCE_PROVIDER=azure-openai
EMBEDDINGS_PROVIDER=azure-openai
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

Azure auth uses `DefaultAzureCredential` — run `az login` locally or assign
Managed Identity in Azure Container Apps.

### Additional variables for Azure OpenAI mode

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | — | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | `gpt-4o-mini` | Chat deployment name |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | `text-embedding-3-small` | Embedding deployment |

---

## Azure AI Foundry mode

```bash
INFERENCE_PROVIDER=foundry
EMBEDDINGS_PROVIDER=foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<hub>.api.azureml.ms/api/projects/<project>
AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_AI_FOUNDRY_EMBEDDING_DEPLOYMENT=text-embedding-3-small
# Optional: override the resource base URL for embeddings
# AZURE_AI_FOUNDRY_RESOURCE_ENDPOINT=https://<resource>.openai.azure.com
```

---

## Build, test, and quality gates

```bash
cd src/dotnet

# Build (warnings-as-errors)
dotnet build --configuration Release

# Tests (40 tests, no network required)
dotnet test

# Format check
dotnet format --verify-no-changes

# Vulnerability scan
dotnet list package --vulnerable --include-transitive
```

---

## Docker build

From the **repo root** (so `data/` can be copied into the image):

```bash
docker build -f src/dotnet/Dockerfile -t zava-api-dotnet .
docker run --rm -p 8080:8080 \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  zava-api-dotnet
```

---

## HTTP API

All routes match the shared contract (identical to the Python track).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | `{"status":"ok"}` |
| GET | `/agents` | List of `{key, name, description}` objects |
| POST | `/chat` | `{message, agent?, sessionId?}` → `{reply, agent, citations[], traceId}` |
| POST | `/chat/stream` | SSE stream of `data: {event, ...}` lines |

### POST /chat example

```json
// Request
{
  "message": "What's Zava's return policy?",
  "agent": "concierge",
  "sessionId": "session-abc-123"
}

// Response
{
  "reply": "Zava offers a 30-day return policy...",
  "agent": "concierge",
  "citations": ["policies/returns.md"],
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

### POST /chat/stream example (SSE)

```
data: {"event":"start","agent":"merchandiser","traceId":"..."}

data: {"event":"token","text":"The ZavaRun Pro "}
data: {"event":"token","text":"features built-in GPS..."}

data: {"event":"end"}
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Zava Minimal API                    │
│  GET /health  GET /agents  POST /chat  /stream   │
└─────────────────┬───────────────────────────────┘
                  │
          ┌───────┴────────┐
          │  AgentRegistry │
          └───────┬────────┘
     ┌────────────┼──────────┬──────────────┐
     ▼            ▼          ▼              ▼
  Concierge  Merchandiser  Operations   Trust
  (RAG+FAQ)  (Products)  (Orders/Ops)  (Compliance)
                    \        /
                    Orchestrator
                  (triage + handoff)
                        │
               ┌────────┴────────┐
               │ InferenceFactory │  INFERENCE_PROVIDER
               │  github /        │  azure-openai /
               │  azure-openai /  │  foundry
               │  foundry         │
               └────────┬────────┘
                        │
              GitHub Models / Azure OpenAI / Foundry
```

---

## Module B audit evidence

The `trust` agent's `generate_evidence` tool assembles audit evidence for the
**AI Applications on Microsoft Azure** Advanced Specialization (controls B.1.1–B.4.2).

Call it via:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"generate evidence report","agent":"trust"}'
```
