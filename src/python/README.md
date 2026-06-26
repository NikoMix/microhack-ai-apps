# Zava AI Agent Platform — Python Track

FastAPI application exposing the Zava multi-agent API, built on the
**Microsoft Agent Framework** (`agent-framework` 1.9.x). Runs fully locally
with **GitHub Models** (free) or switches to **Azure OpenAI** / **Azure AI
Foundry** via a single environment variable.

---

## Architecture

```text
POST /chat
    └─► Orchestrator agent (HandoffWorkflow)
            ├─► Concierge   (get_order · get_product · search_knowledge · create_return)
            ├─► Merchandiser (search_products · get_reviews · sales_trends)
            ├─► Operations  (get_inventory · parse_supplier_doc · restock_suggestion)
            └─► Trust       (content_safety_check · policy_lookup · generate_evidence)
```

Every response carries a real **OpenTelemetry `traceId`** for observability.

---

## Quick-start — GitHub Models mode (no Azure required)

```bash
# 1. Clone and enter the Python src directory
cd src/python

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux / macOS

# 3. Install dependencies (including dev tools)
pip install -e ".[dev]"

# 4. Copy and fill in the template
cp .env.example .env
# Edit .env: set GITHUB_TOKEN to a PAT with models:read scope
# (https://github.com/settings/tokens)
# INFERENCE_PROVIDER and EMBEDDINGS_PROVIDER default to "github"

# 5. Start the server
uvicorn app.main:app --reload

# 6. Verify
curl http://localhost:8000/health     # {"status":"ok"}
curl http://localhost:8000/agents     # list of agents
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"What is the returns policy?"}'
```

> **Without a token**: `/health` and `/agents` respond immediately.  
> `/chat` will return a 503 with a descriptive error (no LLM available).

---

## Azure mode

### Azure OpenAI

```bash
# Set in .env (or Container Apps environment variables):
INFERENCE_PROVIDER=azure-openai
EMBEDDINGS_PROVIDER=azure-openai
AZURE_OPENAI_ENDPOINT=https://<account>.openai.azure.com
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2025-04-01-preview
# Auth: DefaultAzureCredential — no key needed.
# Run: az login  (or set AZURE_CLIENT_ID for managed identity)
uvicorn app.main:app --reload
```

### Azure AI Foundry

```bash
INFERENCE_PROVIDER=foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<project>.services.ai.azure.com/api/projects/<name>
AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT=gpt-4o-mini
uvicorn app.main:app --reload
```

---

## Seeding Azure stores

```bash
# Set COSMOS_ENDPOINT, POSTGRES_HOST, AZURE_SEARCH_ENDPOINT etc. in .env
# Auth: DefaultAzureCredential (az login first)
python scripts/seed.py
```

---

## Docker

```bash
# Build from REPO ROOT (so data/ is accessible)
docker build -f src/python/Dockerfile -t zava-api-python .

# Run in github mode (mount data for local mode)
docker run -p 8000:8000 \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  zava-api-python
```

---

## Quality gates

```bash
# Lint + format
ruff check app/ tests/ && ruff format --check app/ tests/

# Type check
mypy app/

# Tests (no network — LLM is mocked)
pytest

# Vulnerability scan
pip-audit

# Security scan
bandit -r app/ -c pyproject.toml
```

---

## HTTP API

| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/health` | — | `{"status":"ok"}` |
| GET | `/agents` | — | `[{"key","name","description"}]` |
| POST | `/chat` | `{"message","agent?","sessionId?"}` | `{"reply","agent","citations":[],"traceId"}` |
| POST | `/chat/stream` | same | SSE token stream |

`agent` omitted ⇒ orchestrator triages. Every reply includes `traceId` (OTel).

---

## Environment variables reference

| Variable | Default | Description |
|---|---|---|
| `INFERENCE_PROVIDER` | `github` | Chat provider: `github` \| `azure-openai` \| `foundry` |
| `EMBEDDINGS_PROVIDER` | `github` | Embeddings provider: same options |
| `GITHUB_TOKEN` | — | PAT with `models:read` (GitHub Models mode) |
| `GITHUB_MODELS_ENDPOINT` | `https://models.github.ai/inference` | GitHub Models base URL |
| `GITHUB_MODELS_CHAT_MODEL` | `openai/gpt-4o-mini` | Chat model |
| `GITHUB_MODELS_EMBEDDING_MODEL` | `openai/text-embedding-3-small` | Embedding model |
| `AZURE_OPENAI_ENDPOINT` | — | Azure OpenAI endpoint |
| `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` | — | Foundry project endpoint |
| `COSMOS_ENDPOINT` | — | Cosmos DB endpoint |
| `POSTGRES_HOST` | — | PostgreSQL host |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | — | App Insights telemetry |
| `DATA_DIR` | auto-resolved | Path to `data/` seed directory |

---

## Module B evidence (B.1.1–B.4.2)

The `trust` agent's `generate_evidence` tool assembles evidence artifacts for
the *AI Applications on Microsoft Azure* Advanced Specialization audit. Call:

```json
POST /chat
{"message": "Generate evidence for control B.1.1", "agent": "trust"}
```
