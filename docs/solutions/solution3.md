# Solution 3 — Deploy to Azure with azd

> **Facilitator note:** This is the longest lab (55 min), dominated by `azd provision` (~15 min)
> and `azd deploy` (~10 min). Brief students to start `azd provision` immediately and read the
> output while it runs. Pre-provision on your own subscription as a demo fallback.

## Expected command outputs

### azd provision --preview (truncated)

```text
Previewing infrastructure changes for environment 'zava-dev' in subscription 'Visual Studio Enterprise'

PLANNED CHANGES:
  + ResourceGroup: rg-zava-dev (eastus)
  + ManagedIdentity: id-zava-dev
  + KeyVault: kv-zava-dev
      purgeProtectionEnabled: true
  + ContainerRegistry: crzavadev
      anonymousPullEnabled: false
  + ContainerAppsEnvironment: cae-zava-dev
  + ContainerApp: ca-api-python
  + ContainerApp: ca-api-dotnet
  + ContainerApp: ca-mcp-zava
  + AIFoundryHub: ai-zava-dev
  + AIFoundryProject: azd-zava-dev
  + OpenAI: oai-zava-dev
      Deployment: gpt-4o-mini (2024-07-18, Standard)
      Deployment: text-embedding-3-small (2024-02-01, Standard)
  + AISearch: srch-zava-dev
  + DocumentIntelligence: di-zava-dev
  + ContentSafety: cs-zava-dev
  + CosmosDB: cosmos-zava-dev
      database: zava
      disableLocalAuth: true
  + PostgreSQL: pg-zava-dev
      database: zava
      extension: pgvector
  + LogAnalytics: law-zava-dev
  + ApplicationInsights: appi-zava-dev

Total: 19 resources to create.
```

### azd env get-values (after provision)

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
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SERVICE_API_PYTHON_ENDPOINT=https://ca-api-python.happycoast-abc12345.eastus.azurecontainerapps.io
SERVICE_API_DOTNET_ENDPOINT=https://ca-api-dotnet.happycoast-abc12345.eastus.azurecontainerapps.io
SERVICE_MCP_ZAVA_ENDPOINT=https://ca-mcp-zava.happycoast-abc12345.eastus.azurecontainerapps.io
```

### azd deploy output

```text
(✓) Done: Deploying service api-python
      Endpoint: https://ca-api-python.happycoast-abc12345.eastus.azurecontainerapps.io

(✓) Done: Deploying service api-dotnet
      Endpoint: https://ca-api-dotnet.happycoast-abc12345.eastus.azurecontainerapps.io

(✓) Done: Deploying service mcp-zava
      Endpoint: https://ca-mcp-zava.happycoast-abc12345.eastus.azurecontainerapps.io
```

### Deployed API health check

```json
{ "status": "ok" }
```

### Chat call against Azure endpoint (with Foundry grounding)

```json
{
  "reply": "Zava's return policy allows returns within 90 days for smart garments provided the sensor module is intact.",
  "agent": "concierge",
  "citations": [
    {
      "source": "zava-knowledge/returns.md-chunk-001",
      "chunk": "Smart garments may be returned within 90 days...",
      "score": 0.94
    }
  ],
  "traceId": "9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f"
}
```

## Resource inventory export

```bash
az resource list -g rg-zava-dev -o table
```

```text
Name                  ResourceType                                     Location
--------------------  -----------------------------------------------  --------
id-zava-dev           Microsoft.ManagedIdentity/userAssignedIdentities  eastus
kv-zava-dev           Microsoft.KeyVault/vaults                         eastus
crzavadev             Microsoft.ContainerRegistry/registries            eastus
cae-zava-dev          Microsoft.App/managedEnvironments                 eastus
ca-api-python         Microsoft.App/containerApps                       eastus
ca-api-dotnet         Microsoft.App/containerApps                       eastus
ca-mcp-zava           Microsoft.App/containerApps                       eastus
ai-zava-dev           Microsoft.MachineLearningServices/workspaces      eastus
oai-zava-dev          Microsoft.CognitiveServices/accounts              eastus
srch-zava-dev         Microsoft.Search/searchServices                   eastus
di-zava-dev           Microsoft.CognitiveServices/accounts              eastus
cs-zava-dev           Microsoft.CognitiveServices/accounts              eastus
cosmos-zava-dev       Microsoft.DocumentDB/databaseAccounts             eastus
pg-zava-dev           Microsoft.DBforPostgreSQL/flexibleServers         eastus
law-zava-dev          Microsoft.OperationalInsights/workspaces          eastus
appi-zava-dev         Microsoft.Insights/components                     eastus
```

_This table is the `b21-resource-inventory-lab3.txt` evidence artifact._

## Filled evidence artifacts

### b21-resource-inventory-lab3.txt

_Contents: the `az resource list` table above, plus:_

```text
ACR PILLAR MAPPING:
AI Services:  oai-zava-dev, srch-zava-dev, di-zava-dev, cs-zava-dev, ai-zava-dev
App Platform: crzavadev, cae-zava-dev, ca-api-python, ca-api-dotnet, ca-mcp-zava
Data:         cosmos-zava-dev, pg-zava-dev
```

## Common failure modes

| Failure | Root cause | Fix |
|---------|-----------|-----|
| `Insufficient privileges` | Missing `User Access Administrator` | Assign UAA at subscription scope |
| Key Vault name conflict | KV names globally unique | Use `azd env new` with a shorter/different name |
| Container App 502 | App crashed on startup | `az containerapp logs show -n ca-api-python -g rg-zava-dev --follow` |
| `azd deploy` slow (> 20 min) | Large Docker image | Ensure `.dockerignore` excludes tests and node_modules |
| Cosmos DB 403 | MI role not assigned | Check `Cosmos DB Built-in Data Contributor` on the account |
