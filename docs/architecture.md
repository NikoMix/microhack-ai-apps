# Architecture

The Zava AI Agent Platform is a cloud-native, multi-agent system. It is intentionally designed to
exercise **all three Advanced Specialization ACR pillars** while following Azure Well-Architected and
AI-app best practices (managed identity everywhere, no keys, OpenTelemetry, IaC with azd + Bicep AVM).

## Logical architecture

```mermaid
flowchart TB
  subgraph Client
    UI[Web chat / Store associate app]
  end
  subgraph Edge[App Platform pillar]
    APIM[API Management]
    ACA[Azure Container Apps Environment]
    APIPY[api-python<br/>FastAPI + agent-framework]
    APIDN[api-dotnet<br/>Minimal API + Microsoft.Agents.AI]
    MCP[mcp-zava<br/>MCP server]
  end
  subgraph Agents[Microsoft Agent Framework]
    ORCH[Orchestrator]
    CON[Concierge]
    MER[Merchandiser]
    OPS[Operations]
    TRU[Trust & Compliance]
  end
  subgraph AIsvC[AI Services pillar]
    FND[Azure AI Foundry project]
    AOAI[Azure OpenAI<br/>gpt-4o-mini + embeddings]
    SR[Azure AI Search]
    DI[Document Intelligence]
    CS[Content Safety]
    GHM[GitHub Models<br/>free/dev]
  end
  subgraph Data[Data pillar]
    COS[(Cosmos DB<br/>products / orders / customers)]
    PG[(PostgreSQL Flexible<br/>pgvector knowledge)]
  end
  subgraph Platform[Cross-cutting]
    KV[Key Vault]
    MI[User-assigned Managed Identity]
    LAW[Log Analytics]
    AI[Application Insights]
  end

  UI --> APIM --> ACA
  ACA --> APIPY & APIDN
  APIPY & APIDN --> ORCH
  ORCH --> CON & MER & OPS & TRU
  CON --> SR & COS
  MER --> PG & COS
  OPS --> DI & COS
  TRU --> CS
  CON & MER & OPS & TRU --> FND
  FND --> AOAI
  APIPY & APIDN -. dev mode .-> GHM
  APIPY & APIDN --> MCP
  ACA -. telemetry .-> AI --> LAW
  MI --> COS & PG & SR & DI & CS & KV & AOAI & FND
```

## Modular inference

```mermaid
flowchart LR
  A[Agent / tool] --> P{InferenceProvider}
  P -->|github| G[GitHub Models<br/>OpenAI-compatible]
  P -->|azure-openai| AO[Azure OpenAI<br/>Managed Identity]
  P -->|foundry| F[Azure AI Foundry<br/>AIProjectClient]
```

A single factory resolves chat + embedding clients from `INFERENCE_PROVIDER` /
`EMBEDDINGS_PROVIDER`. Agents are written once against the framework's chat-client abstraction, so
the provider swap is invisible to agent logic. Default `github` keeps Labs 0–2 free.

## Request flow (a customer asks about a return)

```mermaid
sequenceDiagram
  participant U as User
  participant API as API (py/.NET)
  participant O as Orchestrator
  participant C as Concierge
  participant T as Trust
  participant S as AI Search
  participant X as Cosmos DB
  U->>API: POST /chat {message}
  API->>O: route(message)
  O->>C: handoff (intent = support)
  C->>S: search_knowledge("returns policy")
  C->>X: get_order(orderId)
  C->>T: content_safety_check(draft reply)
  T-->>C: safe
  C-->>API: reply + citations + traceId
  API-->>U: 200 {reply, citations, traceId}
```

## Pillar → service mapping (drives ACR — B.2.1)

| Pillar | Azure services in this build |
|---|---|
| **AI Services** | Azure AI Foundry, Azure OpenAI, Azure AI Search, Document Intelligence, Content Safety |
| **App Platform** | Azure Container Apps, Azure Container Registry, API Management, GitHub + Copilot |
| **Data** | Azure Cosmos DB, Azure Database for PostgreSQL (pgvector) |

## Security & operations baseline

- **Identity:** one user-assigned **Managed Identity**; **DefaultAzureCredential** in code; **no keys**.
- **Secrets:** **Key Vault** (purge protection on); local dev via git-ignored `.env`.
- **Network/data:** Cosmos & Storage key-auth disabled; ACR anonymous pull disabled.
- **Observability:** OpenTelemetry traces/metrics/logs → **Application Insights**; every API
  response carries a `traceId`.
- **IaC:** **azd + Bicep (Azure Verified Modules)**, latest API versions, validated with
  `azd provision --preview`.

This page is also the basis for the **B.1.1 architecture-diagram** evidence artifact (see
`docs/evidence-templates/`).
