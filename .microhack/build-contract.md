# Build Contract — Zava AI MicroHack (Module B, Train-the-Trainer)

> **Read this first.** Every workstream session MUST conform to this contract so the parallel
> tracks integrate cleanly. Do not change paths, env-var names, the HTTP API, or service names
> without coordinating. Owner of this file: the orchestrator session.

## 1. Scenario — "Zava"

**Zava** is Microsoft's 2025 fictional **intelligent athletic apparel** retailer (the successor to
Contoso/Fabrikam). In this microhack, Zava is building an **AI Agent Platform on Azure** to power
its enterprise. Learners build that platform. The story is coherent end-to-end and every lab output
doubles as **audit evidence** for the *AI Applications on Microsoft Azure* Advanced Specialization
(Module B controls B.1.1–B.4.2).

Three internal Zava "customers" (used for the B.2.2 customer-diversity lesson):
`Zava Retail Stores`, `Zava eCommerce`, `Zava Wholesale`.

## 2. Agents (identical across Python and .NET tracks)

Built with **Microsoft Agent Framework** (`agent-framework` Python / `Microsoft.Agents.AI` .NET).

| Agent key | Role | Tools (functions) | Enterprise topic / pillar |
|---|---|---|---|
| `concierge` | Customer support: order status, returns, product Q&A (RAG) | `get_order`, `get_product`, `search_knowledge`, `create_return` | Support · AI + Data |
| `merchandiser` | Product insights & recommendations | `search_products`, `get_reviews`, `sales_trends` | Merchandising · AI + Data |
| `operations` | Supply chain & inventory; supplier doc parsing | `get_inventory`, `parse_supplier_doc`, `restock_suggestion` | Ops · AI + Data |
| `trust` | Content safety, governance, **audit-evidence generation** | `content_safety_check`, `policy_lookup`, `generate_evidence` | Trust/Compliance · AI |
| `orchestrator` | Triage/route to the right agent (handoff workflow) | n/a (Agent Framework workflow) | Platform |

RAG grounding uses Zava knowledge (policies, product catalog, reviews, supplier docs) indexed in
**Azure AI Search** and/or **PostgreSQL pgvector**.

## 3. Modular inference contract (REQUIRED)

A provider abstraction selects the chat + embedding backend at runtime via env vars. **No image
generation** anywhere (so GitHub Models / AOAI / Foundry are all valid). Default = GitHub Models
(free) so labs run with zero Azure cost; flip a single env var to use Azure.

```
INFERENCE_PROVIDER = github | azure-openai | foundry      # default: github
EMBEDDINGS_PROVIDER = github | azure-openai | foundry     # default: github
```

### GitHub Models (default)
```
GITHUB_TOKEN=<PAT or Actions token with models:read>
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference
GITHUB_MODELS_CHAT_MODEL=openai/gpt-4o-mini
GITHUB_MODELS_EMBEDDING_MODEL=openai/text-embedding-3-small
```
GitHub Models is **OpenAI-compatible** → use the framework's OpenAI chat client with `base_url`/
endpoint override + the token. Verify the current endpoint/model ids against GitHub Models docs.

### Azure OpenAI
```
AZURE_OPENAI_ENDPOINT=https://<acct>.openai.azure.com
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=<latest GA>
```
Auth: **DefaultAzureCredential / Managed Identity — NEVER an API key.**

### Azure AI Foundry (recommended Azure path)
```
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<proj>.services.ai.azure.com/api/projects/<name>
AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT=gpt-4o-mini
```
Auth: DefaultAzureCredential. Prefer the `AIProjectClient` → `.AsAIAgent()` / Foundry agent pattern
per Azure AI-app best practices (call `get_azure_bestpractices_ai_app`).

**Embedding dimension = 1536** everywhere (`text-embedding-3-small`): pgvector `vector(1536)` and
AI Search vector fields must match.

## 4. HTTP API contract (identical for both tracks)

Both `api-python` and `api-dotnet` expose the SAME REST API so labs, tests, and the UI are
track-agnostic:

| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/health` | — | `{ "status": "ok" }` |
| GET | `/agents` | — | `[{ "key","name","description" }]` |
| POST | `/chat` | `{ "message", "agent?", "sessionId?" }` | `{ "reply", "agent", "citations":[], "traceId" }` |
| POST | `/chat/stream` | same | SSE token stream (optional but recommended) |

`agent` omitted ⇒ the `orchestrator` triages. Always return a `traceId` (OpenTelemetry trace id).

## 5. Repository layout & ownership (disjoint → conflict-free)

```
/                      README, LICENSE, .gitignore, .editorconfig, mkdocs.yml      [orchestrator]
.devcontainer/         polyglot dev container                                       [orchestrator]
.github/               copilot-instructions, dependabot, workflows, ISSUE_TEMPLATE  [orchestrator]
.github/agents/        GitHub Copilot custom agents                                 [WS4]
.github/skills/        Copilot skills                                               [WS4]
.microhack/            this contract                                                [orchestrator]
data/                  Zava seed data (catalog, policies, reviews, suppliers)       [orchestrator]
docs/ (top-level)      index, overview, agenda, architecture, module-b-mapping      [orchestrator]
docs/facilitator-guide/ TTT facilitator guide                                       [WS5]
docs/labs/             student lab guides                                           [WS6]
docs/solutions/        lab solutions                                                 [WS6]
docs/evidence-templates/ Module B evidence templates                                [WS6]
docs/cert-crosswalk.md AZ-204/AI-102/DP-420/AZ-400 mapping                          [WS6]
slides/                Marp decks                                                    [WS5]
infra/                 azd + Bicep (AVM)                                             [WS1]
azure.yaml             azd config                                                    [WS1]
src/python/            Python track (FastAPI + Agent Framework)                      [WS2]
src/dotnet/            .NET track (Minimal API + Microsoft.Agents.AI)               [WS3]
src/mcp-zava/          custom Zava MCP server                                        [WS4]
mcp.json               MCP server config for VS Code/Copilot                         [WS4]
```

**Rule:** a session edits ONLY its owned paths. Commit, then `git push -u origin HEAD`.

## 6. Azure resource contract (WS1 infra — Bicep AVM, all managed identity, no keys)

azd `services` in `azure.yaml`: `api-python` → `src/python`, `api-dotnet` → `src/dotnet`,
`mcp-zava` → `src/mcp-zava` (all host: containerapp, Dockerfile in each dir).

Provision: Container Apps Env + 3 Container Apps · Azure Container Registry (no anon pull) ·
Azure AI Foundry (hub+project) + model deployments `gpt-4o-mini`, `text-embedding-3-small` ·
Azure AI Search · Document Intelligence · Content Safety · Cosmos DB (database `zava`; containers
`products`,`orders`,`customers`; **disable key auth**, AAD RBAC) · PostgreSQL Flexible Server
(`zava` db, pgvector) · Key Vault (purge protection ON) · Log Analytics + Application Insights ·
User-assigned Managed Identity with least-privilege role assignments · API Management (optional
front door). Use **latest API versions**; validate with `azd provision --preview` / `bicep lint`.
Do NOT actually deploy in CI (cost) — validation only.

### Canonical env vars emitted by infra (azd outputs)
```
COSMOS_ENDPOINT, COSMOS_DATABASE=zava
POSTGRES_HOST, POSTGRES_DB=zava, POSTGRES_PORT=5432
AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_INDEX=zava-knowledge
AZURE_DOCINTEL_ENDPOINT
AZURE_CONTENTSAFETY_ENDPOINT
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT, AZURE_OPENAI_ENDPOINT
AZURE_KEY_VAULT_ENDPOINT
APPLICATIONINSIGHTS_CONNECTION_STRING
AZURE_CLIENT_ID  (user-assigned MI for the container apps)
```

## 7. Data contract (orchestrator owns `data/`)

- `data/products.json` — Zava smart-apparel catalog (id, name, category, price, sizes, smart features, description).
- `data/reviews.json` — product reviews (productId, rating, text).
- `data/orders.json` — sample orders (orderId, customer, items, status).
- `data/customers.json` — the 3 Zava business units.
- `data/policies/*.md` — returns, warranty, sustainability, sizing, smart-garment-care.
- `data/suppliers/*.md` — sample supplier docs for Document Intelligence labs.

Apps load this seed data for local/GitHub-Models mode (no Azure required) and to seed Azure stores.

## 8. Coding standards & quality gates (ALL sessions)

- **Latest dependencies, zero known vulnerabilities.** Pin to newest stable. Python: `pip-audit` +
  `bandit`. .NET: `dotnet list package --vulnerable --include-transitive`. JS (if any): `npm audit`.
- **OSS / no paid-license libraries only.** If none fits, build it.
- **Auth:** DefaultAzureCredential / Managed Identity everywhere. No keys, no secrets in code.
- **Lint/format:** Python `ruff` (lint+format) + `mypy`; .NET analyzers + `dotnet format` + nullable
  enable + warnings-as-errors where sane; Markdown `markdownlint`. `.editorconfig` is authoritative.
- **Observability:** OpenTelemetry traces/metrics/logs → Application Insights; emit `traceId`.
- **Tests:** pytest (Python) / xUnit (.NET); cover the inference abstraction + agent tools + API.
- **Docs:** every `src/*` dir has a README with run instructions for BOTH GitHub-Models and Azure modes.

## 9. Module B coverage map (what each control needs from the build)

| Control | Delivered by |
|---|---|
| B.1.1 Azure AI Implementation | Whole app (AI on Azure) + capstone evidence (case study, architecture diagram, capability statement) auto-generated by the `trust` agent |
| B.2.1 ACR Performance | App spans all 3 pillars; ACR worksheet + Partner Center export walkthrough |
| B.2.2 Customer Diversity | 3 Zava business units + association-types (DPOR/PAL/CSP) lesson |
| B.3.1 Certifications | Lab ↔ exam crosswalk (AZ-204, AI-102, DP-420, AZ-400) |
| B.4.1 Audit Readiness | Evidence package + index produced by capstone; pre-audit checklist |
| B.4.2 Partner Onboarding | Onboarding pack + delivery templates produced as lab outputs |
