# Zava AI Agent Platform — Infrastructure (`infra/`)

Bicep IaC using **Azure Verified Modules (AVM)**, deployed with **Azure Developer CLI (azd)**.
Owned by WS1 (Infrastructure). Conforms to `.microhack/build-contract.md §6`.

## Architecture

All resources use **Managed Identity / DefaultAzureCredential** — no API keys, no connection strings
with secrets, no local auth. A single **User-Assigned Managed Identity** (UAMI) is granted
least-privilege roles on every service.

```text
Subscription
└── rg-zava-<env>
    ├── id-zava-<token>            User-Assigned Managed Identity
    ├── law-zava-<token>           Log Analytics Workspace
    ├── appi-zava-<token>          Application Insights (workspace-based)
    ├── stzava<token>              Storage Account (AI Foundry Hub artifacts)
    ├── kv-zava-<token>            Key Vault (RBAC mode, purge protection ON)
    ├── cr-zava<token>             Container Registry (admin off, anon pull off)
    ├── ais-zava-<token>           AI Services (gpt-4o-mini + text-embedding-3-small)
    ├── di-zava-<token>            Document Intelligence
    ├── cs-zava-<token>            Content Safety
    ├── hub-zava-<token>           AI Foundry Hub
    ├── proj-zava-<token>          AI Foundry Project
    ├── srch-zava-<token>          Azure AI Search (local auth off)
    ├── cosmos-zava-<token>        Cosmos DB (key auth off, AAD RBAC)
    │   └── zava (db)
    │       ├── products (container)
    │       ├── orders (container)
    │       └── customers (container)
    ├── psql-zava-<token>          PostgreSQL Flexible (AAD auth, pgvector)
    │   └── zava (database)
    └── cae-zava-<token>           Container Apps Environment
        ├── ca-api-python          FastAPI + agent-framework
        ├── ca-api-dotnet          ASP.NET Minimal API + Microsoft.Agents.AI
        └── ca-mcp-zava            Zava MCP server
```

## Security baseline

| Control | Setting |
|---|---|
| ACR admin | Disabled |
| ACR anonymous pull | Disabled |
| Cognitive Services local auth | Disabled (all accounts) |
| Cosmos DB key auth | Disabled |
| AI Search local auth | Disabled |
| Key Vault purge protection | ON |
| Key Vault auth mode | RBAC (no access policies) |
| PostgreSQL password auth | Disabled |
| PostgreSQL AAD auth | Enabled; UAMI is DB admin |
| Storage shared key access | Disabled |
| Container Apps identity | User-Assigned MI |

## Prerequisites

```bash
# Install Azure Developer CLI
winget install microsoft.azd   # or: brew install azd / curl -fsSL https://aka.ms/install-azd.sh | bash

# Install Azure CLI + Bicep
az bicep install

# Log in
az login
azd auth login
```

## Set required secrets

```bash
# PostgreSQL admin password (used only during provisioning; app uses AAD auth)
azd env set POSTGRES_ADMIN_PASSWORD "YourStr0ngP@ssword!"

# Optional: customize admin username (default: pgadmin)
azd env set POSTGRES_ADMIN_LOGIN "pgadmin"
```

## Provision (create all Azure resources)

```bash
# Preview what will be created — NO ACTUAL DEPLOYMENT
azd provision --preview

# Actually provision
azd provision
```

## Deploy applications (after provisioning)

```bash
# Build Docker images, push to ACR, update Container Apps
azd deploy
```

## Full lifecycle

```bash
# Provision + deploy in one step
azd up

# Check status / outputs
azd env get-values

# Tear down (delete resource group and all resources)
azd down --purge   # --purge required to delete Key Vault with purge protection
```

## Validate Bicep (CI — no Azure credentials needed)

```bash
# Install Bicep CLI
az bicep install

# Build (type-checks, resolves AVM module schemas)
bicep build infra/main.bicep

# Lint (best-practice checks, security rules)
bicep lint infra/main.bicep
```

The `.github/workflows/infra-validate.yml` runs both on every PR touching `infra/` or `azure.yaml`.

## AVM modules used

| Resource | AVM module | Version |
|---|---|---|
| User-Assigned MI | `avm/res/managed-identity/user-assigned-identity` | 0.5.1 |
| Log Analytics | `avm/res/operational-insights/workspace` | 0.15.1 |
| Application Insights | `avm/res/insights/component` | 0.7.2 |
| Key Vault | `avm/res/key-vault/vault` | 0.13.3 |
| Container Registry | `avm/res/container-registry/registry` | 0.12.1 |
| Cognitive Services | `avm/res/cognitive-services/account` | 0.15.0 |
| AI Foundry Hub/Project | `avm/res/machine-learning-services/workspace` | 0.13.2 |
| Azure AI Search | `avm/res/search/search-service` | 0.12.2 |
| Cosmos DB | `avm/res/document-db/database-account` | 0.19.0 |
| PostgreSQL Flexible | `avm/res/db-for-postgre-sql/flexible-server` | 0.15.4 |
| Container Apps Env | `avm/res/app/managed-environment` | 0.13.3 |
| Container App | `avm/res/app/container-app` | 0.22.1 |

## azd outputs (canonical env vars)

These are emitted from `main.bicep` and injected into every Container App automatically by azd.

| Variable | Source |
|---|---|
| `COSMOS_ENDPOINT` | Cosmos DB account endpoint |
| `COSMOS_DATABASE` | `zava` (constant) |
| `POSTGRES_HOST` | PostgreSQL server FQDN |
| `POSTGRES_DB` | `zava` (constant) |
| `POSTGRES_PORT` | `5432` (constant) |
| `AZURE_SEARCH_ENDPOINT` | AI Search endpoint |
| `AZURE_SEARCH_INDEX` | `zava-knowledge` (constant) |
| `AZURE_DOCINTEL_ENDPOINT` | Document Intelligence endpoint |
| `AZURE_CONTENTSAFETY_ENDPOINT` | Content Safety endpoint |
| `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` | AI Foundry Project endpoint |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_KEY_VAULT_ENDPOINT` | Key Vault URI |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights connection string |
| `AZURE_CLIENT_ID` | UAMI client ID → `DefaultAzureCredential` |

## Cost estimate (lab / training)

Approximate hourly cost for the default configuration (burstable tiers):

| Resource | SKU | ~$/hr |
|---|---|---|
| Container Apps (3 × Consumption) | Consumption | ~$0.00 (pay per request) |
| Container Registry | Basic | ~$0.007 |
| AI Services | S0 | ~$0.00 (pay per call) |
| AI Search | Basic | ~$0.10 |
| Cosmos DB | 400 RU/s serverless | ~$0.00 (pay per op) |
| PostgreSQL | Burstable B2ms | ~$0.07 |
| Key Vault | Standard | ~$0.00 (pay per op) |
| Log Analytics | PerGB2018 | ~$0.00 (low ingestion) |

**Total**: ~$0.18/hr when idle. Run `azd down --purge` after labs to eliminate ongoing cost.

## Modular inference

The Container Apps are pre-configured with `INFERENCE_PROVIDER=azure-openai`.
To switch providers without re-deploying infrastructure:

```bash
# GitHub Models (free, for local dev)
azd env set INFERENCE_PROVIDER github
azd env set EMBEDDINGS_PROVIDER github
azd deploy  # pushes env var update only

# Azure AI Foundry
azd env set INFERENCE_PROVIDER foundry
azd deploy
```

## Production hardening checklist

- [ ] Set `publicNetworkAccess: 'Disabled'` on all services
- [ ] Add Private Endpoints + Private DNS zones
- [ ] Enable VNet integration for Container Apps Environment
- [ ] Set AI Foundry Hub `isolationMode: 'AllowOnlyApprovedOutbound'`
- [ ] Enable zone-redundant deployment (PostgreSQL, Cosmos DB)
- [ ] Upgrade PostgreSQL to `GeneralPurpose` tier
- [ ] Set ACR to `Premium` SKU (private endpoint support)
- [ ] Enable Customer-Managed Keys for data-at-rest encryption
- [ ] Set up Azure Monitor alerts and action groups
- [ ] Enable Microsoft Defender for all resource types

## Module B evidence

This infrastructure delivers **B.1.1 (Azure AI Implementation)** evidence by provisioning all three
ACR pillars: AI Services (Foundry, OpenAI, Search, Doc Intel, Content Safety), App Platform
(Container Apps, ACR), and Data (Cosmos DB, PostgreSQL). See `docs/module-b-mapping.md`.
