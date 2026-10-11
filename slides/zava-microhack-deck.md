---
marp: true
theme: default
paginate: true
footer: "Zava AI MicroHack · AI Applications on Azure Advanced Specialization · Module B"
style: |
  :root {
    --navy:  #0a1628;
    --blue:  #0078d4;
    --green: #00b050;
    --amber: #f0a500;
    --mid:   #1e2d42;
    --font:  "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    --mono:  "Cascadia Code", "Fira Code", Consolas, monospace;
  }
  section {
    font-family: var(--font); font-size: 26px; line-height: 1.55;
    background: var(--navy); color: #fff;
    padding: 55px 75px; width: 1280px; height: 720px; box-sizing: border-box;
  }
  section::after { font-size: .52em; color: rgba(255,255,255,.35); }
  h1 { font-size: 1.75em; font-weight: 700; border-bottom: 3px solid var(--blue);
       padding-bottom: .12em; margin: 0 0 .4em; color: #fff; }
  h2 { font-size: 1.2em; font-weight: 600; color: var(--blue); margin: .55em 0 .25em; }
  h3 { font-size: 1.0em; font-weight: 600; color: var(--green); margin: .45em 0 .2em; }
  section.lead {
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; text-align: center;
    background: linear-gradient(155deg, var(--navy) 0%, var(--mid) 100%);
    padding: 60px;
  }
  section.lead h1 { font-size: 2.15em; border: none; margin-bottom: .3em; }
  section.lead h2 { color: rgba(255,255,255,.72); font-weight: 400; font-size: 1.15em; margin-top: 0; }
  section.lead p { color: rgba(255,255,255,.78); font-size: .88em; margin: .3em 0; }
  section.section-header {
    display: flex; flex-direction: column; justify-content: center;
    background: linear-gradient(135deg, var(--blue) 0%, #005ba1 100%);
  }
  section.section-header h1 { font-size: 2.0em; border-color: rgba(255,255,255,.45); margin-bottom: .3em; }
  section.section-header p { color: rgba(255,255,255,.82); font-size: .9em; }
  section.lab-intro {
    background: linear-gradient(135deg, #0e3a1e 0%, var(--mid) 100%);
    border-left: 8px solid var(--green);
  }
  section.lab-intro h1 { color: var(--green); border-color: rgba(0,176,80,.45); }
  section.lab-intro h2 { color: rgba(0,176,80,.85); }
  code { font-family: var(--mono); font-size: .82em; background: rgba(255,255,255,.1);
         padding: .1em .3em; border-radius: 3px; }
  pre { background: rgba(0,0,0,.42); border-left: 3px solid var(--blue);
        padding: .7em 1em; border-radius: 4px; margin: .6em 0; overflow: hidden; }
  pre code { background: transparent; font-size: .76em; padding: 0; }
  table { border-collapse: collapse; width: 100%; font-size: .8em; margin: .5em 0; }
  thead th { background: var(--blue); color: #fff; padding: .35em .65em;
             text-align: left; font-weight: 600; }
  tbody tr:nth-child(even) { background: rgba(255,255,255,.055); }
  tbody td { padding: .3em .65em; border-bottom: 1px solid rgba(255,255,255,.08); vertical-align: top; }
  ul { padding-left: 1.3em; }
  li { margin-bottom: .3em; }
  ul li::marker { color: var(--green); }
  strong { color: var(--green); font-weight: 700; }
  em { color: #7ec8e3; font-style: normal; font-weight: 600; }
  blockquote {
    border-left: 4px solid var(--amber); padding: .45em 1em;
    background: rgba(240,165,0,.1); border-radius: 0 4px 4px 0;
    margin: .7em 0; font-size: .88em;
  }
  footer { font-size: .5em; color: rgba(255,255,255,.3); }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# 🏃 Zava AI MicroHack

## Build Enterprise AI Agents on Microsoft Azure

*1-day · Instructor-Led · Train-the-Trainer*

**AI Applications on Microsoft Azure — Advanced Specialization · Module B**

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 👩‍🏫 For the Trainer

## Using This Deck

- **One deck, one day** — follow agenda order; section headers signal topic shifts
- **🟩 Green slides** = lab introductions; keep them short and action-oriented
- **💡 Callouts** (*like this*) = trainer asides, not student content
- Slide notes (PDF comments) contain **detailed talk-track** cues
- The [Facilitator Guide](../docs/facilitator-guide/index.md) has full timing and demos

> 🔗 **Facilitator Guide** → `docs/facilitator-guide/`
> 🔗 **Labs** → `docs/labs/`

---

## Today's Agenda at a Glance

| Time | Block | Type |
|---|---|---|
| 08:30 | Welcome & TTT orientation | Trainer |
| 08:45 | Why AI Apps on Azure · Zava story | Lecture |
| 09:10 | **Lab 0** — Environment & GitHub Models | Lab |
| 09:30 | Agentic foundations · Agent Framework | Lecture |
| 09:50 | **Lab 1** — Your first Zava agent | Lab |
| 10:55 | Grounding & RAG | Lecture |
| 11:10 | **Lab 2** — Ground it (RAG + swap to Azure) | Lab |
| 12:45 | Azure platform · azd · IaC | Lecture |
| 13:05 | **Lab 3** — Deploy to Azure | Lab |
| 14:00 | Data agents · Cosmos DB · PostgreSQL | Lecture |
| 14:15 | **Lab 4** — Data agents | Lab |
| 15:15 | Trust, safety & governance | Lecture |
| 15:30 | **Lab 5** — Trust & observability | Lab |
| 16:15 | Build with AI · GitHub agents · MCP | Lecture |
| 16:30 | **Lab 6** — Capstone + evidence pack | Lab |
| 17:15 | Evidence review & audit readiness | Lecture |
| 17:30 | TTT debrief & close | Trainer |

---

## Housekeeping

- **Audience:** partner engineers (you'll re-deliver this as TTT)
- **Pre-reqs:** GitHub account + Copilot licence · Docker · VS Code / Dev Container

> 💡 *No Azure subscription needed for Labs 0–2 — GitHub Models is **free***.

### Two tracks — pick one

| 🐍 Python | 🟦 .NET |
|---|---|
| FastAPI + `agent-framework` | ASP.NET Minimal API + `Microsoft.Agents.AI` |
| `src/python/` | `src/dotnet/` |

Both tracks → **same agents, same HTTP API, same labs.**

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 1 · Why AI Apps on Azure

The Advanced Specialization, Module B, and the Zava story

---

## The Advanced Specialization

**AI Applications on Microsoft Azure** is Microsoft's partner validation for:

- ✅ Demonstrated **technical capability** delivering AI solutions on Azure
- ✅ **Revenue** across the 3 ACR pillars (AI Services · App Platform · Data)
- ✅ **Customer diversity** (≥ 3 customers via DPOR / PAL / CSP)
- ✅ **Certified staff** (AZ-204, AI-102, DP-420, AZ-400)
- ✅ **Audit-ready evidence package** with structured documentation

> 🎯 This microhack builds the technical capability **and** teaches you to assemble the evidence.

---

## Module B Controls at a Glance

| Control | What the auditor checks | This microhack delivers |
|---|---|---|
| **B.1.1** | AI solution live on Azure | Labs 1–6: multi-agent app on Azure AI Foundry/OpenAI/Search |
| **B.2.1** | ACR across 3 pillars | Services span AI · App Platform · Data (see architecture) |
| **B.2.2** | ≥ 3 unique customers | 3 Zava business units → customer-diversity lesson |
| **B.3.1** | Certified individuals | Lab-to-exam crosswalk (AZ-204, AI-102, DP-420, AZ-400) |
| **B.4.1** | Organised evidence package | `trust` agent + capstone assemble the evidence index |
| **B.4.2** | Onboarding & delivery assets | Lab outputs generalised into reusable templates |

---

## The 3 ACR Pillars

```text
┌────────────────────────────────────────────────────────────────┐
│  AI Services pillar                                            │
│  Azure AI Foundry · Azure OpenAI · AI Search                  │
│  Document Intelligence · Content Safety                       │
├────────────────────────────────────────────────────────────────┤
│  App Platform pillar                                           │
│  Azure Container Apps · Container Registry                    │
│  API Management · GitHub + Copilot                            │
├────────────────────────────────────────────────────────────────┤
│  Data pillar                                                   │
│  Azure Cosmos DB · Azure Database for PostgreSQL (pgvector)   │
└────────────────────────────────────────────────────────────────┘
```

> Each lab maps to one or more pillars — see `docs/module-b-mapping.md`

---

## Meet Zava 🧢

**Zava** — Microsoft's 2025 fictional *intelligent athletic apparel* retailer.
Smart garments: connected running shirts, recovery leggings, adaptive jackets.

### Three business units (= 3 diverse customers for B.2.2)

| Business unit | What it does |
|---|---|
| **Zava Retail Stores** | Physical stores + store associates |
| **Zava eCommerce** | Web & mobile storefront |
| **Zava Wholesale** | B2B sales to gyms & sports teams |

> Zava's platform team (you) is building an **AI Agent Platform** on Azure.
> Every lab output doubles as **audit evidence** for Module B.

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 2 · Solution Architecture

The Zava AI Agent Platform end-to-end

---

## The Zava AI Agent Platform

```text
  User / Store Associate
         │
    API Management
         │
  Azure Container Apps
    ┌────┴────┐
    api-python  api-dotnet
         │
    Orchestrator Agent
    ┌────┼────┬─────┐
    ▼    ▼    ▼     ▼
Concierge  Merchandiser  Operations  Trust & Compliance
    │          │             │            │
AI Search   PostgreSQL  Doc. Intel.  Content Safety
Cosmos DB   Cosmos DB   Cosmos DB   OpenTelemetry
         └────────────────────────────────┘
                    Azure AI Foundry
              (gpt-4o-mini + text-embedding-3-small)
```

*dev mode →* **GitHub Models** (free, OpenAI-compatible)

---

## The 5 Agents

| Agent | Helps… | Tools |
|---|---|---|
| **Orchestrator** | everyone | routes requests to specialists |
| **Concierge** | customers & associates | `get_order`, `search_knowledge`, `create_return` |
| **Merchandiser** | merchandising team | `search_products`, `get_reviews`, `sales_trends` |
| **Operations** | ops & supply chain | `get_inventory`, `parse_supplier_doc`, `restock_suggestion` |
| **Trust & Compliance** | the whole org | `content_safety_check`, `policy_lookup`, `generate_evidence` |

---

## The HTTP API Contract

Both tracks (Python + .NET) expose **the same REST API**:

| Method | Path | Response |
|---|---|---|
| `GET` | `/health` | `{ "status": "ok" }` |
| `GET` | `/agents` | `[{ key, name, description }]` |
| `POST` | `/chat` | `{ reply, agent, citations[], traceId }` |
| `POST` | `/chat/stream` | SSE token stream |

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your returns policy?"}'
```

> Every response includes a **`traceId`** (OpenTelemetry trace ID).

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 3 · Modular Inference

GitHub Models · Azure OpenAI · Azure AI Foundry

---

## Three Providers — One Switch

```bash
# GitHub Models (default — free, no Azure needed)
INFERENCE_PROVIDER=github
GITHUB_TOKEN=<PAT with models:read>

# Azure OpenAI
INFERENCE_PROVIDER=azure-openai
AZURE_OPENAI_ENDPOINT=https://<acct>.openai.azure.com

# Azure AI Foundry (recommended Azure path)
INFERENCE_PROVIDER=foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<proj>.services.ai.azure.com/api/projects/<name>
```

> A **single factory** resolves the chat + embedding client at runtime.
> Agents are written **once** against the abstraction — provider swap is invisible.

---

## GitHub Models (Default for Labs 0–2)

- **Endpoint:** `https://models.github.ai/inference`
- **Auth:** `GITHUB_TOKEN` (PAT with `models:read` scope)
- **OpenAI-compatible** — use the OpenAI client with `base_url` override
- **Models used:**
  - Chat: `openai/gpt-4o-mini`
  - Embeddings: `openai/text-embedding-3-small` (dim = 1536)
- **Cost: $0** — free tier for Copilot subscribers

> Perfect for teaching: no Azure subscription, no cost, instant start.

---

## Azure AI Foundry (Recommended Azure Path)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
# Use AIProjectClient as the Agent Framework's inference provider
```

| Provider | Auth | When to use |
|---|---|---|
| GitHub Models | `GITHUB_TOKEN` | Labs 0–2, demos, CI |
| Azure OpenAI | `DefaultAzureCredential` | Enterprise, existing AOAI |
| **Azure AI Foundry** | `DefaultAzureCredential` | **Recommended for production** |

> **No API keys. No secrets in code.** Managed Identity everywhere.

---

<!-- _class: lab-intro -->
<!-- _paginate: false -->

# 🟩 Lab 0 — Environment & GitHub Models

**⏱ 09:10–09:30 (20 min)**

---

## Lab 0 — What You'll Do

1. **Open** the repository in the dev container
   `Dev Containers: Reopen in Container` in VS Code
2. **Export** your GitHub Personal Access Token
   `export GITHUB_TOKEN=<PAT with models:read>`
3. **Run** the API on GitHub Models (zero Azure cost)
   ```bash
   # Python:
   cd src/python && make run
   # .NET:
   cd src/dotnet && dotnet run
   ```
4. **Call** the health and agents endpoints
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/agents
   ```
5. **Evidence checkpoint:** dev environment ready ✅

> 🔗 `docs/labs/lab-00-environment.md`

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 4 · Agentic Foundations

Microsoft Agent Framework · Agents vs Workflows · Python & .NET

---

## What Is an AI Agent?

An AI agent **perceives** a request, **reasons** using an LLM, and **acts** via tools — in a loop until it achieves the goal.

```text
   ┌─────────────────────────────────────────┐
   │               Agent loop                │
   │                                         │
   │  Perception  →  Reasoning (LLM)         │
   │                     │                   │
   │            Tool call(s) ←──────────┐   │
   │                     │              │   │
   │            Observation  ───────────┘   │
   │                     │                   │
   │            Final response               │
   └─────────────────────────────────────────┘
```

- **Tools** = typed functions the LLM can call (`get_order`, `search_knowledge`, …)
- **Memory** = session history + vector-retrieved context
- **Handoff** = one agent delegates to another (orchestrator pattern)

---

## Microsoft Agent Framework

Two SDKs, one model:

| | Python | .NET |
|---|---|---|
| **Package** | `agent-framework` | `Microsoft.Agents.AI` |
| **API host** | FastAPI | ASP.NET Minimal API |
| **Path** | `src/python/` | `src/dotnet/` |
| **Inference** | `InferenceProvider` factory | Same abstraction |

### Key concepts

- **`Agent`** — has a system prompt, a set of tools, and an inference provider
- **`Tool`** — a typed function registered on an agent; called when the LLM decides
- **`Workflow`** — deterministic multi-step process (not LLM-driven; used by Orchestrator)
- **`Handoff`** — Orchestrator transfers context to a specialist agent

---

## Python: Concierge Agent (sketch)

```python
from agent_framework import Agent, tool

class ConciergeAgent(Agent):
    system_prompt = "You are Zava's customer support agent..."

    @tool
    async def get_order(self, order_id: str) -> dict:
        """Retrieve order status from Cosmos DB."""
        return await self.cosmos.get_order(order_id)

    @tool
    async def search_knowledge(self, query: str) -> list[str]:
        """RAG search over policies and product catalog."""
        return await self.search.query(query)
```

> The agent uses the **InferenceProvider** abstraction — swap `INFERENCE_PROVIDER` and nothing else changes.

---

## .NET: Concierge Agent (sketch)

```csharp
public class ConciergeAgent : AgentBase
{
    protected override string SystemPrompt =>
        "You are Zava's customer support agent...";

    [AgentTool("get_order", "Retrieve order status")]
    public async Task<OrderResult> GetOrder(string orderId)
        => await _cosmos.GetOrderAsync(orderId);

    [AgentTool("search_knowledge", "RAG search over policies")]
    public async Task<IEnumerable<string>> SearchKnowledge(string query)
        => await _search.QueryAsync(query);
}
```

> `Microsoft.Agents.AI` uses attributes to register tools — identical semantics to Python.

---

<!-- _class: lab-intro -->
<!-- _paginate: false -->

# 🟩 Lab 1 — Your First Zava Agent

**⏱ 09:50–10:40 (50 min)**

---

## Lab 1 — What You'll Build

1. **Implement** the `ConciergeAgent` with tools: `get_order`, `search_knowledge`, `create_return`
2. **Wire** the agent into the `/chat` endpoint (orchestrator routes to it)
3. **Test** with: `"What's the status of order ORD-001?"`
4. **Verify** the response includes `traceId` (OpenTelemetry trace)
5. **Observe** tool calls in the application logs

### Expected outcome

```json
{
  "reply": "Order ORD-001 is shipped and expected...",
  "agent": "concierge",
  "citations": [],
  "traceId": "4bf5122f2681..."
}
```

> **Module B:** B.1.1 — AI on Azure (GitHub Models for now)
> 🔗 `docs/labs/lab-01-first-agent.md`

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 5 · Grounding & RAG

Embeddings · Azure AI Search · pgvector · Citations

---

## Why Ground Your Agents?

Without grounding, an agent can **hallucinate** policies, prices, and order details.

**RAG (Retrieval-Augmented Generation):**

```text
  User query
      │
  Embed query → vector (1536-dim)
      │
  Vector search → top-k chunks
      │
  Augment prompt with chunks
      │
  LLM generates grounded reply
      │
  Return reply + citations[]
```

**Zava's knowledge sources:**

- Policies: returns, warranty, sustainability, sizing, smart-garment care
- Product catalog: names, descriptions, smart features, reviews
- Supplier documents: parsed by Document Intelligence

---

## Azure AI Search Pipeline

```text
  data/policies/*.md
  data/products.json       →  Document Intelligence (PDF/DOCX)
  data/suppliers/*.md             │
                                  ▼
                         Chunk + embed
                         (text-embedding-3-small, 1536-dim)
                                  │
                                  ▼
                         Azure AI Search index
                         (zava-knowledge, vector + keyword)
                                  │
                                  ▼
                         search_knowledge() tool
```

> Hybrid search = **keyword + vector** → better recall for product names + semantic queries.

---

## pgvector as Alternative

For teams preferring PostgreSQL over managed search:

```sql
-- One-time setup
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge (
    id         SERIAL PRIMARY KEY,
    content    TEXT,
    embedding  vector(1536),     -- matches text-embedding-3-small
    source     TEXT
);

-- Semantic search
SELECT content, source,
       embedding <=> $1::vector AS distance
FROM   knowledge
ORDER  BY distance
LIMIT  5;
```

> **`EMBEDDINGS_PROVIDER`** controls which service generates embeddings —
> same factory pattern as inference.

---

## Citations and Trustworthiness

Every RAG response includes a `citations[]` array:

```json
{
  "reply": "Zava's returns policy allows returns within 30 days...",
  "citations": [
    { "source": "policies/returns.md", "chunk": "Returns within 30 days..." }
  ],
  "traceId": "..."
}
```

- **Citations = audit trail** for content-safety review
- The `trust` agent's `content_safety_check` tool validates the draft reply
  *before* it is returned to the user
- Trace the full flow in **Application Insights** via `traceId`

---

<!-- _class: lab-intro -->
<!-- _paginate: false -->

# 🟩 Lab 2 — Ground It

**⏱ 11:10–12:00 (50 min)**

---

## Lab 2 — What You'll Do

1. **Index** Zava policies and catalog into Azure AI Search (or pgvector locally)
2. **Upgrade** `ConciergeAgent.search_knowledge` to query the index
3. **Verify** citations appear in the response
4. **Swap** `INFERENCE_PROVIDER` to `azure-openai` or `foundry`
   → confirm same behaviour, different backend
5. **Test** semantic query: `"Can I return smart leggings after 45 days?"`

### Evidence checkpoint

- Architecture diagram (B.1.1) ✅
- First grounded agent call log ✅

> **Module B:** B.1.1 (AI grounding), B.2.1 (AI Search = AI Services pillar)
> 🔗 `docs/labs/lab-02-rag.md`

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 6 · Azure Platform

azd · Bicep/AVM · Container Apps · Managed Identity

---

## `azd up` — Everything in One Command

```bash
# 1. Login
az login && azd auth login

# 2. Provision + deploy
azd up
# → Provisions all Azure resources via Bicep
# → Builds container images + pushes to ACR
# → Deploys to Container Apps
# → Emits all AZURE_* env vars as azd outputs

# 3. Verify
curl https://<app>.azurecontainerapps.io/health
```

> **`azure.yaml`** defines three services: `api-python`, `api-dotnet`, `mcp-zava`
> All run as **Container Apps** with a shared Container Apps Environment.

---

## Bicep + Azure Verified Modules (AVM)

```bicep
// infra/main.bicep (abbreviated)
module cosmosAccount 'br/public:avm/res/document-db/database-account:0.8.1' = {
  params: {
    name:                       'cosmos-zava-${suffix}'
    location:                   location
    disableLocalAuth:           true    // key auth OFF — RBAC only
    sqlRoleAssignmentsPrincipalIds: [managedIdentity.outputs.principalId]
  }
}
```

### Key security standards

- `disableLocalAuth: true` on Cosmos DB and Storage (key auth off)
- `anonymousPullEnabled: false` on ACR
- Key Vault: `enablePurgeProtection: true`
- All auth via **user-assigned Managed Identity** — `DefaultAzureCredential`

---

## What Gets Provisioned

```text
Container Apps Environment
  ├── api-python (FastAPI)
  ├── api-dotnet (Minimal API)
  └── mcp-zava   (MCP server)
       │
       ├── Azure Container Registry (ACR)
       ├── Azure AI Foundry hub + project
       │     └── gpt-4o-mini · text-embedding-3-small
       ├── Azure AI Search (zava-knowledge index)
       ├── Document Intelligence
       ├── Content Safety
       ├── Cosmos DB  (zava: products / orders / customers)
       ├── PostgreSQL (zava db + pgvector)
       ├── Key Vault  (purge-protection ON)
       └── Log Analytics + Application Insights
```

> **User-assigned Managed Identity** holds all role assignments.
> **No connection strings in code.** No secrets. Just `DefaultAzureCredential`.

---

<!-- _class: lab-intro -->
<!-- _paginate: false -->

# 🟩 Lab 3 — Deploy to Azure

**⏱ 13:05–14:00 (55 min)**

---

## Lab 3 — What You'll Do

1. **Run** `azd up` — provision + deploy the full platform
2. **Verify** all Container Apps are running: `api-python`, `api-dotnet`, `mcp-zava`
3. **Check** Application Insights: confirm traces are flowing
4. **Call** the deployed `/chat` endpoint with a real query
5. **Confirm** `traceId` in the response links to a live trace in App Insights
6. **Explore** the Managed Identity role assignments in the portal

### Evidence checkpoint

- Azure deployment screenshot (B.1.1, B.2.1) ✅
- Application Insights trace (B.4.1) ✅

> **Module B:** B.1.1, B.2.1 (App Platform pillar: Container Apps, ACR, API Management)
> 🔗 `docs/labs/lab-03-deploy.md`

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 7 · Data Agents

Cosmos DB for catalog & orders · PostgreSQL + pgvector for knowledge

---

## Cosmos DB — Catalog, Orders, Customers

Database: `zava` | Three containers:

| Container | Key fields | Agent(s) |
|---|---|---|
| `products` | id, name, category, price, smart-features | Merchandiser |
| `orders` | orderId, customer, items, status | Concierge |
| `customers` | id, businessUnit, associationType | Orchestrator |

```python
# Example: Merchandiser's get_reviews tool
async def get_reviews(self, product_id: str) -> list[Review]:
    query = "SELECT * FROM c WHERE c.productId = @id"
    return await self.cosmos.query(container="products", query=query,
                                   params=[{"name": "@id", "value": product_id}])
```

> **Auth:** `DefaultAzureCredential` + Cosmos DB RBAC. **`disableLocalAuth: true`**.

---

## PostgreSQL + pgvector — Knowledge Store

```sql
-- Knowledge table (pgvector)
CREATE TABLE knowledge (
    id        SERIAL PRIMARY KEY,
    content   TEXT        NOT NULL,
    source    TEXT        NOT NULL,
    embedding vector(1536) NOT NULL   -- text-embedding-3-small
);

-- Concierge search_knowledge tool executes:
SELECT content, source,
       embedding <=> $1::vector AS distance
FROM   knowledge
ORDER  BY distance
LIMIT  5;
```

- Local mode: connects to PostgreSQL in dev container
- Production: **Azure Database for PostgreSQL Flexible Server**
  - Auth: `DefaultAzureCredential` (password-free, AAD auth)
  - Connection string injected as `POSTGRES_HOST` by azd

---

<!-- _class: lab-intro -->
<!-- _paginate: false -->

# 🟩 Lab 4 — Data Agents

**⏱ 14:15–15:00 (45 min)**

---

## Lab 4 — What You'll Build

1. **Implement** `MerchandiserAgent`:
   - Tools: `search_products`, `get_reviews`, `sales_trends`
   - Data source: Cosmos DB `products` container
2. **Implement** `OperationsAgent`:
   - Tools: `get_inventory`, `parse_supplier_doc`, `restock_suggestion`
   - Data sources: Cosmos DB `products` + Document Intelligence
3. **Test** with: `"Which running shirts are low in stock?"` → routes to Operations
4. **Test** with: `"Show me reviews for the Zava Alpha leggings"` → routes to Merchandiser
5. **Evidence checkpoint:** data-grounded agent traces in App Insights ✅

> **Module B:** B.1.1, B.2.1 (Data pillar: Cosmos DB + PostgreSQL), B.2.2 (business units)
> 🔗 `docs/labs/lab-04-data-agents.md`

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 8 · Trust, Safety & Governance

Content Safety · OpenTelemetry · OWASP for Agents · Evaluations

---

## The Trust & Compliance Agent

Every response goes through a **safety gate** before it reaches the user:

```text
  Agent draft reply
         │
  TrustAgent.content_safety_check()
         │
  Azure Content Safety API
         │
    ┌────┴────┐
  SAFE     FLAGGED
    │           │
  Return     Block + log + alert
  to user
```

**Tools:**

- `content_safety_check(text)` — calls Azure Content Safety
- `policy_lookup(topic)` — retrieves governance policies
- `generate_evidence(controls)` — assembles the Module B evidence package

---

## OpenTelemetry → Application Insights

```python
# Every API response carries a traceId
from opentelemetry import trace

tracer = trace.get_tracer("zava.api")

with tracer.start_as_current_span("chat.request") as span:
    span.set_attribute("agent", selected_agent)
    span.set_attribute("message_len", len(message))
    reply = await agent.run(message)
    span.set_attribute("reply_len", len(reply))
```

- **Traces** → Application Insights (via OTLP exporter)
- **Metrics:** request latency, token usage, safety flag rate
- **Logs:** structured JSON to Log Analytics
- **Dashboard:** App Insights workbook shows end-to-end flows

> `traceId` in every `/chat` response links user-visible output to the full trace.

---

## OWASP for AI Agents

Top threats and how Zava mitigates them:

| OWASP Risk | Zava Mitigation |
|---|---|
| LLM01 — Prompt Injection | Input validation + Content Safety gate |
| LLM02 — Insecure Output Handling | Citations enforced; structured output types |
| LLM06 — Sensitive Info Disclosure | No PII in logs; Key Vault for secrets |
| LLM08 — Excessive Agency | Orchestrator scopes tool access per agent |
| LLM09 — Over-reliance | Citations + confidence scores exposed to user |

> The `trust` agent also runs **evaluations** on sampled responses to detect drift.

---

<!-- _class: lab-intro -->
<!-- _paginate: false -->

# 🟩 Lab 5 — Trust & Observability

**⏱ 15:30–16:15 (45 min)**

---

## Lab 5 — What You'll Do

1. **Implement** `TrustAgent.content_safety_check` using **Azure Content Safety**
2. **Wire** the safety gate into every agent's response path
3. **Verify** a flagged message is blocked (test with `"harmful content test"`)
4. **Add** OpenTelemetry spans to the `/chat` endpoint
5. **View** the trace in Application Insights: see agent handoff, tool calls, and safety check
6. **Run** a basic evaluation: call `trust.generate_evidence(["B.4.1"])` and inspect the output

### Evidence checkpoint

- Safety gate log (B.4.1) ✅
- App Insights trace screenshot (B.4.1) ✅

> **Module B:** B.4.1 (audit readiness: safety gate + tracing)
> 🔗 `docs/labs/lab-05-trust.md`

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 9 · Build with AI

GitHub Copilot Custom Agents · Skills · MCP Servers

---

## GitHub Copilot Custom Agents

Extend Copilot with domain-specific agents checked in to `.github/agents/`:

```yaml
# .github/agents/zava-architect.yml
name: ZavaArchitect
description: |
  Expert on the Zava AI Agent Platform architecture, Azure services,
  Module B controls, and the Agent Framework patterns.
model: gpt-4o
instructions: |
  You are the Zava platform architect. Help developers extend agents,
  review IaC, and map new features to Module B controls.
tools:
  - type: code_search
  - type: file_search
```

- Custom agents appear in **GitHub Copilot Chat** as `@ZavaArchitect`
- They have **deep repo context** — see your code, not just the question
- Combine with **Copilot skills** for action-taking capabilities

---

## Copilot Skills

Skills extend agents with **callable actions** in `.github/skills/`:

```yaml
# .github/skills/generate-evidence.yml
name: GenerateEvidence
description: Compile Module B evidence artifacts from lab outputs
parameters:
  - name: controls
    type: string[]
    description: List of Module B control IDs (e.g. ["B.1.1", "B.4.1"])
```

**In practice:**
`@ZavaArchitect /generate-evidence controls:["B.1.1","B.4.1"]`
→ calls the skill → calls the `trust` agent's `generate_evidence` tool
→ returns the structured evidence package

---

## MCP Servers — Model Context Protocol

MCP makes **any data source or tool** accessible to AI models:

```text
  AI Model (Copilot / Agent)
          │
     MCP client
          │
     MCP server  ←── Zava MCP Server (src/mcp-zava/)
          │
   ┌──────┼──────┐
   ▼      ▼      ▼
Products Orders Policies
(Cosmos) (Cosmos) (AI Search)
```

**`mcp.json`** configures MCP servers for VS Code and GitHub Copilot:

```json
{
  "servers": {
    "zava": {
      "url": "http://localhost:3100/mcp",
      "description": "Zava catalog, orders, and policies"
    }
  }
}
```

---

<!-- _class: lab-intro -->
<!-- _paginate: false -->

# 🟩 Lab 6 — Capstone: GitHub Agents, Skills & MCP + Evidence Pack

**⏱ 16:30–17:15 (45 min)**

---

## Lab 6 — What You'll Build

1. **Extend** the Zava platform with a new GitHub Copilot custom agent
2. **Register** a skill that calls an agent tool via HTTP
3. **Start** the Zava MCP server and verify Copilot can query Zava products
4. **Run** `trust.generate_evidence(["B.1.1","B.2.1","B.2.2","B.3.1","B.4.1","B.4.2"])`
5. **Review** the generated evidence index — it maps every artifact to its control

---

## Lab 6 — The Evidence Package

The `trust` agent produces a structured **Module B evidence package**:

```text
evidence/
├── index.md              ← control → artifact mapping
├── B.1.1-architecture/
│   ├── architecture-diagram.md
│   └── capability-statement.md
├── B.2.1-acr/
│   └── pillar-worksheet.md
├── B.2.2-customers/
│   └── customer-diversity-table.md
├── B.3.1-certs/
│   └── cert-crosswalk.md
├── B.4.1-audit/
│   └── evidence-index.md
└── B.4.2-onboarding/
    └── onboarding-pack.md
```

> **This is what a real partner submits for the Advanced Specialization audit.**
> Lab 6 gives you a **starter pack** you can adapt for a live engagement.

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 10 · Evidence Review & Audit Readiness

Module B wrap-up · Customer diversity · Cert crosswalk

---

## Evidence-as-You-Go — The Full Picture

| Lab | Evidence produced | Module B control |
|---|---|---|
| 0 | Dev environment ready | — |
| 1 | Working AI agent + trace | B.1.1 |
| 2 | Grounded agent + citations + provider swap | B.1.1, B.2.1 |
| 3 | Azure deployment + App Insights trace | B.1.1, B.2.1 |
| 4 | Data-grounded agents (Cosmos + Postgres) | B.1.1, B.2.1, B.2.2 |
| 5 | Safety gate + observability | B.4.1 |
| 6 | Full evidence package (all controls) | B.1.1–B.4.2 |

> The `trust` agent's `generate_evidence` assembles, indexes, and packages all artifacts.

---

## Customer Diversity (B.2.2)

Auditors require **≥ 3 unique customers** associated via DPOR, PAL, or CSP.

| Business unit | Association type | What the lesson teaches |
|---|---|---|
| Zava Retail Stores | DPOR (Digital Partner of Record) | How to associate via Partner Center |
| Zava eCommerce | PAL (Partner Admin Link) | How to link your ID to a subscription |
| Zava Wholesale | CSP (Cloud Solution Provider) | How to manage via Partner Center |

> The `B.2.2-customers/customer-diversity-table.md` artifact gives you a template
> to document your real customer associations.

---

## Certification Crosswalk (B.3.1)

Each lab maps to real exam objectives:

| Lab | AZ-204 | AI-102 | DP-420 | AZ-400 |
|---|:---:|:---:|:---:|:---:|
| 0 Environment | ● | | | ● |
| 1 First agent | ● | ● | | |
| 2 RAG | | ● | ● | |
| 3 Deploy | ● | | | ● |
| 4 Data agents | | ● | ● | |
| 5 Trust | | ● | | ● |
| 6 Capstone | ● | ● | ● | ● |

> B.3.1 requires **5 certified individuals** across these exams. Lab outputs
> help you build a study plan and track progress. See `docs/cert-crosswalk.md`.

---

<!-- _class: section-header -->
<!-- _paginate: false -->

# 11 · TTT Debrief & Close

Re-delivery checklist · Delivery tips · Next steps

---

## TTT Re-Delivery Checklist

**Before your delivery:**

- [ ] Fork or clone the repo; confirm the dev container runs cleanly
- [ ] Get a GitHub PAT with `models:read` — test it with a `curl` to GitHub Models
- [ ] Optional: provision your own Azure subscription with `azd provision`
- [ ] Run Labs 0–2 yourself end-to-end (< 60 min) to spot issues
- [ ] Review the Facilitator Guide timing and confirm you have ≥ 7 hours
- [ ] Prepare the A/V checklist: projector, HDMI, breakout rooms (if virtual), Miro board

**Day-of:**

- [ ] Open the repo in a dev container 30 min before start
- [ ] Test the GitHub Models endpoint
- [ ] Have the solution branches ready as fallbacks for stuck attendees

> Full checklist: `docs/facilitator-guide/ttt-notes.md`

---

## Delivery Tips — What Works Well

### ✅ Do

- **Show, don't just tell** — live-code the agent skeleton before attendees start each lab
- **Use the Orchestrator as the "magic demo"** — route a message and show agent selection
- **Let them get stuck (briefly)** — `docs/facilitator-guide/pitfalls.md` has the fixes
- **Connect every slide to the evidence** — "this is the artifact that satisfies B.1.1"
- **End each lab with the evidence checkpoint** — it reinforces the audit mindset

### ❌ Avoid

- Don't rush lectures to fit more lab time — labs have built-in recovery paths
- Don't skip the modular inference demo — it's the key differentiator
- Don't troubleshoot individual laptops during lecture time — flag + return

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 🏁 Thank You

## What You Built Today

- ✅ A production-pattern **multi-agent AI platform** on Azure
- ✅ **Modular inference** across GitHub Models, AOAI, and AI Foundry
- ✅ **Grounded, safe, observable** agents with full telemetry
- ✅ **GitHub Copilot custom agents**, skills, and MCP integration
- ✅ A **Module B evidence starter pack** ready to adapt for real engagements

---

**Next steps:**

1. Re-deliver this microhack to your team or customer
2. Adapt the evidence pack for a real Advanced Specialization audit
3. Explore the cert crosswalk and schedule certification exams
4. Contribute back — issues + PRs welcome at `NikoMix/microhack-ai-apps`

> 🔗 Facilitator Guide: `docs/facilitator-guide/`
> 🔗 Labs: `docs/labs/`
> 🔗 Module B: `docs/module-b-mapping.md`
