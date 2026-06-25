# Lab 3 — Deploy to Azure with azd

> **Estimated time:** 55 minutes
> **Module B controls:** B.1.1 (Azure AI Implementation), B.2.1 (ACR Performance — all three pillars),
> B.3.1 (Certifications), B.4.2 (Partner Onboarding — IaC as delivery template)

## Learning objectives

By the end of this lab you will be able to:

1. Use `azd provision` to deploy the full Zava infrastructure (Bicep / Azure Verified Modules).
2. Identify the services deployed in each ACR pillar (AI, App Platform, Data).
3. Use `azd deploy` to containerise and publish both the Python and .NET APIs to Container Apps.
4. Verify the deployed API with health and chat calls against the Azure endpoints.
5. Explain how Managed Identity and Key Vault replace every hardcoded credential.

## Prerequisites

- Lab 2 complete.
- An Azure subscription where you have **Contributor** and **User Access Administrator** rights
  (needed to assign roles to the Managed Identity).
- `az login` completed: `az account show`.
- `azd` installed (`azd version` should show 1.9 or later — already in the dev container).

---

## Background — azd and the Zava infra

The `azure.yaml` at the repository root defines three azd services:

| azd service | Source | Hosts |
|-------------|--------|-------|
| `api-python` | `src/python` | Azure Container App |
| `api-dotnet` | `src/dotnet` | Azure Container App |
| `mcp-zava` | `src/mcp-zava` | Azure Container App |

Bicep modules live in `infra/` using **Azure Verified Modules (AVM)** — no custom resource
definitions needed. All Azure resources use **Managed Identity**; no keys anywhere.

---

## Step 1 — Log in to Azure and initialise azd

```bash
az login                     # Azure CLI login (browser opens)
azd auth login               # azd login (may reuse CLI credentials)
azd init --no-prompt         # reads azure.yaml in-place
```

Set a short, unique environment name (this becomes part of the Azure resource names):

```bash
azd env new zava-dev
```

!!! tip "Environment naming"
    Keep it short (≤ 12 chars) and lowercase. Azure resource names like the Container Registry and
    Key Vault derive from this name and have character limits.

---

## Step 2 — Preview the deployment

Run a preflight check without creating any resources:

```bash
azd provision --preview
```

Review the output. You should see ~16 resource types planned:

```text
~ Resource group:         rg-zava-dev
+ Managed Identity:       id-zava-dev
+ Key Vault:              kv-zava-dev  (purge protection: enabled)
+ Container Registry:     crzavadev    (anonymous pull: disabled)
+ Container Apps Env:     cae-zava-dev
+ Container App:          ca-api-python
+ Container App:          ca-api-dotnet
+ Container App:          ca-mcp-zava
+ AI Foundry hub:         ai-zava-dev
+ AI Foundry project:     azd-zava-dev
+ Azure OpenAI:           oai-zava-dev (gpt-4o-mini, text-embedding-3-small)
+ Azure AI Search:        srch-zava-dev (index: zava-knowledge)
+ Document Intelligence:  di-zava-dev
+ Content Safety:         cs-zava-dev
+ Cosmos DB:              cosmos-zava-dev (zava db, key-auth disabled)
+ PostgreSQL:             pg-zava-dev  (zava db, pgvector)
+ Application Insights:   appi-zava-dev
+ Log Analytics:          law-zava-dev
```

!!! note "B.2.1 pillar coverage"
    - **AI Services:** AI Foundry, Azure OpenAI, AI Search, Document Intelligence, Content Safety
    - **App Platform:** Container Apps, Container Registry, API Management
    - **Data:** Cosmos DB, PostgreSQL (pgvector)

    Each of these contributes toward the $15k-per-pillar ACR threshold. See the
    [ACR Pillar Worksheet](../evidence-templates/b21-acr-pillar-worksheet.md).

---

## Step 3 — Provision the infrastructure

```bash
azd provision
```

This takes 8–15 minutes. Watch the live output. Key milestones:

1. Resource group created.
2. Managed Identity and Key Vault deployed.
3. AI Foundry + OpenAI deployments deployed.
4. Container Apps Environment and Registry deployed.
5. Cosmos DB and PostgreSQL deployed.
6. Role assignments applied (MI gets least-privilege roles on every service).

When complete, `azd` writes all endpoints to `.azure/zava-dev/.env`. Inspect them:

```bash
azd env get-values
```

Expected output (truncated):

```dotenv
COSMOS_ENDPOINT=https://cosmos-zava-dev.documents.azure.com:443/
COSMOS_DATABASE=zava
POSTGRES_HOST=pg-zava-dev.postgres.database.azure.com
POSTGRES_DB=zava
POSTGRES_PORT=5432
AZURE_SEARCH_ENDPOINT=https://srch-zava-dev.search.windows.net
AZURE_SEARCH_INDEX=zava-knowledge
AZURE_DOCINTEL_ENDPOINT=https://di-zava-dev.cognitiveservices.azure.com/
AZURE_CONTENTSAFETY_ENDPOINT=https://cs-zava-dev.cognitiveservices.azure.com/
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://azd-zava-dev.services.ai.azure.com/api/projects/zava
AZURE_OPENAI_ENDPOINT=https://oai-zava-dev.openai.azure.com/
AZURE_KEY_VAULT_ENDPOINT=https://kv-zava-dev.vault.azure.net/
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
AZURE_CLIENT_ID=<guid>
```

---

## Step 4 — Deploy the applications

Build the container images and push them to ACR, then deploy to Container Apps:

```bash
azd deploy
```

This builds the Dockerfile in each source directory and pushes to the Container Registry with
Managed Identity (no username/password). Expected output:

```text
Deploying service api-python ... done
  Endpoint: https://ca-api-python.happycoast-XXXX.eastus.azurecontainerapps.io
Deploying service api-dotnet ... done
  Endpoint: https://ca-api-dotnet.happycoast-XXXX.eastus.azurecontainerapps.io
Deploying service mcp-zava   ... done
  Endpoint: https://ca-mcp-zava.happycoast-XXXX.eastus.azurecontainerapps.io
```

Save the Python API endpoint:

```bash
PYTHON_URL=$(azd env get-values | grep SERVICE_API_PYTHON_ENDPOINT | cut -d= -f2-)
echo $PYTHON_URL
```

---

## Step 5 — Seed data to Azure

With the cloud infrastructure running, seed Cosmos DB, PostgreSQL, and AI Search:

=== "Python"

    ```bash
    cd src/python
    # Set env vars from azd outputs
    source <(azd env get-values | sed 's/^/export /')
    INFERENCE_PROVIDER=foundry EMBEDDINGS_PROVIDER=foundry python scripts/seed.py --target azure
    ```

=== ".NET"

    ```bash
    cd src/dotnet
    # PowerShell: export azd env vars
    azd env get-values | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v) }
    dotnet run --project ZavaApi -- --seed-all --target azure
    ```

This seeds:

- Cosmos DB `products`, `orders`, `customers` containers.
- PostgreSQL pgvector `knowledge` table with policy embeddings (1536-dim, `foundry` provider).
- Azure AI Search `zava-knowledge` index with the same vectors.

---

## Step 6 — Verify the deployed API

```bash
# Health check
curl -s "$PYTHON_URL/health" | python -m json.tool

# Chat with the Azure-deployed API
curl -s -X POST "$PYTHON_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Zava return policy?", "agent": "concierge"}' \
  | python -m json.tool
```

The response now has `"reply"` grounded by data from Azure AI Search — verify citations point to
real policy chunks.

---

## Step 7 — Switch inference to Azure AI Foundry

Update `.azure/zava-dev/.env` (or the Container App environment variables) to use Foundry:

```dotenv
INFERENCE_PROVIDER=foundry
EMBEDDINGS_PROVIDER=foundry
```

Redeploy:

```bash
azd deploy --service api-python
```

Repeat the chat call — identical results, now backed by Azure AI Foundry.

---

## Step 8 — View Application Insights

1. Open the [Azure Portal](https://portal.azure.com) → your resource group `rg-zava-dev`.
2. Click **Application Insights** (`appi-zava-dev`).
3. Navigate to **Transaction search** → search for your `traceId` from the previous chat call.
4. Observe the full distributed trace: API → Orchestrator → Concierge → AI Search → Cosmos DB.

---

## Validation checklist

- [ ] `azd provision --preview` shows all 16+ resources without errors.
- [ ] `azd provision` completes; `azd env get-values` shows all canonical env vars.
- [ ] `azd deploy` publishes all three services; endpoints are live.
- [ ] `GET /health` returns `{"status": "ok"}` from the Container App URL.
- [ ] `POST /chat` returns a grounded reply with citations from Azure AI Search.
- [ ] `traceId` from chat response is findable in Application Insights.
- [ ] No API keys in any env var (all use DefaultAzureCredential / Managed Identity).

---

## Evidence checkpoint — B.1.1, B.2.1, B.4.2

| Artifact | What it proves | Control |
|----------|---------------|---------|
| `azd provision --preview` output | IaC deployment of AI on Azure | B.1.1 |
| Resource group screenshot (Portal) | All 3 ACR pillars deployed | B.2.1 |
| Container App endpoint responding | App Platform pillar in production | B.2.1 |
| Application Insights trace | Observability on Azure | B.1.1 |
| `infra/` Bicep modules | Reusable IaC — delivery template | B.4.2 |

> **Action:** Export the resource group ARM inventory (`az resource list -g rg-zava-dev -o table`)
> and save as `evidence/b21-resource-inventory-lab3.txt`. Screenshot the Application Insights
> trace as `evidence/b11-appi-trace-lab3.png`.

---

## Key concepts review

| Concept | Detail |
|---------|--------|
| `azure.yaml` | azd configuration: services → source directories |
| Bicep AVM | Azure Verified Modules — pre-validated IaC building blocks |
| Managed Identity | `AZURE_CLIENT_ID`; no keys anywhere in code or config |
| Key Vault purge protection | Prevents accidental permanent deletion of secrets |
| ACR anonymous pull disabled | Container images require MI auth |
| Cosmos DB key-auth disabled | RBAC-only access via Managed Identity |
| `azd deploy` | Builds Dockerfile → pushes to ACR → updates Container App |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Insufficient privileges` on `azd provision` | Ensure Contributor + User Access Administrator |
| Key Vault name taken | Choose a different `azd env` name (KV names are globally unique) |
| Container App returning 502 | Check logs: `az containerapp logs show -n ca-api-python -g rg-zava-dev` |
| Cosmos DB 403 | Verify MI has `Cosmos DB Built-in Data Contributor` role |
| AI Search 403 | Verify MI has `Search Index Data Contributor` + `Search Service Contributor` |

## Next lab

Proceed to **[Lab 4 — Data agents: Merchandiser & Operations](lab4.md)**.
