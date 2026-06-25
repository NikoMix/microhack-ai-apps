// ─────────────────────────────────────────────────────────────────────────────
// Zava AI Agent Platform — Main Infrastructure Orchestrator
//
// Scope: subscription (creates resource group, then deploys all modules at RG scope)
//
// Provisions (all via Azure Verified Modules):
//   ✓ User-Assigned Managed Identity (single UAMI for all apps)
//   ✓ Log Analytics Workspace + Application Insights (workspace-based)
//   ✓ Storage Account (AI Foundry Hub artifact storage)
//   ✓ Key Vault (RBAC mode, purge protection ON)
//   ✓ Azure Container Registry (admin disabled, anon pull disabled)
//   ✓ AI Services account (AIServices kind, gpt-4o-mini + text-embedding-3-small)
//   ✓ Document Intelligence (FormRecognizer, local auth disabled)
//   ✓ Content Safety (local auth disabled)
//   ✓ AI Foundry Hub + Project (ML workspace, system-assigned MI)
//   ✓ Azure AI Search (local auth disabled, RBAC only)
//   ✓ Cosmos DB NoSQL (local auth disabled, AAD RBAC data plane)
//       databases: zava | containers: products, orders, customers
//   ✓ PostgreSQL Flexible Server (AAD auth, password auth disabled, pgvector)
//       database: zava
//   ✓ Container Apps Environment + 3 Container Apps
//       api-python, api-dotnet, mcp-zava (azd-service-name tagged)
//
// Auth: DefaultAzureCredential / Managed Identity everywhere — NO API keys.
// Validation: bicep build + bicep lint (CI); azd provision --preview (local)
// ─────────────────────────────────────────────────────────────────────────────

targetScope = 'subscription'

// ─── Parameters ──────────────────────────────────────────────────────────────

@description('Name of the Azure Developer CLI environment (e.g. dev, staging). Used for naming and tagging.')
@minLength(1)
@maxLength(32)
param environmentName string

@description('Primary Azure region for all resources.')
@minLength(1)
param location string

@description('PostgreSQL admin username. Only used by the Bicep provisioning plane; the app uses AAD auth.')
@minLength(1)
@maxLength(63)
param postgresAdminLogin string = 'pgadmin'

@secure()
@description('PostgreSQL admin password. Only used during initial provisioning; password auth is disabled afterwards. Set via: azd env set POSTGRES_ADMIN_PASSWORD <value>')
param postgresAdminPassword string

// ─── Variables ────────────────────────────────────────────────────────────────

// Short resource-naming prefix for all Zava resources
var prefix = 'zava'

// Deterministic token derived from subscription + env + location to ensure unique,
// repeatable resource names across deployments. toLower ensures DNS-compatibility.
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Short token suffix used in most names (8 chars → predictable length)
var suffix = take(resourceToken, 8)

var resourceGroupName = 'rg-${prefix}-${environmentName}'

var tags = {
  'azd-env-name': environmentName
  project: 'zava'
  workstream: 'WS1-infra'
  environment: environmentName
  'managed-by': 'azd'
}

// ─── Resource Group ───────────────────────────────────────────────────────────
resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// ─── User-Assigned Managed Identity ──────────────────────────────────────────
// Single UAMI for all Container Apps → DefaultAzureCredential targets this identity.
// All role assignments below grant this identity least-privilege access.
module identity 'modules/identity.bicep' = {
  name: 'identity'
  scope: rg
  params: {
    name: 'id-${prefix}-${suffix}'
    location: location
    tags: tags
  }
}

// ─── Monitoring (Log Analytics + App Insights) ────────────────────────────────
// Deploy first — other modules (Container Apps Env, AI Foundry Hub) depend on these.
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    logAnalyticsName: 'law-${prefix}-${suffix}'
    appInsightsName: 'appi-${prefix}-${suffix}'
    location: location
    tags: tags
  }
}

// ─── Storage Account (required by AI Foundry Hub) ────────────────────────────
// Storage names: 3–24 lowercase alphanumeric only (no hyphens).
// 'st' + 'zava' + 10 hex chars = ~16 chars total ✓
module storage 'modules/storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: 'st${prefix}${take(resourceToken, 10)}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── Key Vault ────────────────────────────────────────────────────────────────
// Name limit: 3–24 chars. 'kv-zava-' (8) + 7 chars = 15 ✓
module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  scope: rg
  params: {
    name: 'kv-${prefix}-${take(resourceToken, 7)}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── Container Registry ───────────────────────────────────────────────────────
// ACR names: 5–50 lowercase alphanumeric only (no hyphens).
// 'cr' + 'zava' + 8 hex chars = 14 chars total ✓
module registry 'modules/registry.bicep' = {
  name: 'registry'
  scope: rg
  params: {
    name: 'cr${prefix}${suffix}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── AI Services (Azure OpenAI + AI Foundry backend) ─────────────────────────
// Deploys gpt-4o-mini (chat) and text-embedding-3-small (1536-dim RAG embeddings).
// INFERENCE_PROVIDER=azure-openai|foundry both target this account.
module aiServices 'modules/aiServices.bicep' = {
  name: 'aiservices'
  scope: rg
  params: {
    name: 'ais-${prefix}-${suffix}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── Document Intelligence ────────────────────────────────────────────────────
// Used by the `operations` agent to parse supplier PDFs and invoices.
module documentIntelligence 'modules/documentIntelligence.bicep' = {
  name: 'documentintelligence'
  scope: rg
  params: {
    name: 'di-${prefix}-${suffix}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── Content Safety ───────────────────────────────────────────────────────────
// Used by the `trust` agent to screen agent replies for harmful content.
module contentSafety 'modules/contentSafety.bicep' = {
  name: 'contentsafety'
  scope: rg
  params: {
    name: 'cs-${prefix}-${suffix}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── AI Foundry Hub + Project ─────────────────────────────────────────────────
// Hub: shared infrastructure (Storage, KV, App Insights, ACR)
// Project: per-use-case experiments and AI agent configurations
// ML workspace names: 3–33 chars.
module aiFoundry 'modules/aiFoundry.bicep' = {
  name: 'aifoundry'
  scope: rg
  params: {
    hubName: 'hub-${prefix}-${suffix}'
    projectName: 'proj-${prefix}-${suffix}'
    location: location
    storageAccountResourceId: storage.outputs.resourceId
    keyVaultResourceId: keyVault.outputs.resourceId
    appInsightsResourceId: monitoring.outputs.appInsightsResourceId
    containerRegistryResourceId: registry.outputs.resourceId
    aiServicesResourceId: aiServices.outputs.resourceId
    aiServicesEndpoint: aiServices.outputs.endpoint
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── Azure AI Search ──────────────────────────────────────────────────────────
// RAG knowledge base for all agents. Index: zava-knowledge (1536-dim vectors).
module aiSearch 'modules/aiSearch.bicep' = {
  name: 'aisearch'
  scope: rg
  params: {
    name: 'srch-${prefix}-${suffix}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── Cosmos DB ────────────────────────────────────────────────────────────────
// NoSQL store for products, orders, customers (operational data for agents).
// Key auth disabled; UAMI gets Cosmos DB Built-in Data Contributor.
module cosmosDb 'modules/cosmosDb.bicep' = {
  name: 'cosmosdb'
  scope: rg
  params: {
    name: 'cosmos-${prefix}-${suffix}'
    location: location
    managedIdentityPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

// ─── PostgreSQL Flexible Server ───────────────────────────────────────────────
// pgvector knowledge store (1536-dim) for semantic search.
// Password auth disabled; UAMI is the AAD admin.
module postgres 'modules/postgres.bicep' = {
  name: 'postgres'
  scope: rg
  params: {
    name: 'psql-${prefix}-${suffix}'
    location: location
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: postgresAdminPassword
    managedIdentityPrincipalId: identity.outputs.principalId
    managedIdentityName: identity.outputs.name
    tags: tags
  }
}

// ─── Container Apps Environment + 3 Apps ─────────────────────────────────────
// Environment links to Log Analytics. Each app is tagged with azd-service-name
// so `azd deploy` knows which container app to update.
module containerApps 'modules/containerApps.bicep' = {
  name: 'containerapps'
  scope: rg
  params: {
    environmentName: 'cae-${prefix}-${suffix}'
    location: location
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    managedIdentityResourceId: identity.outputs.resourceId
    managedIdentityClientId: identity.outputs.clientId
    acrLoginServer: registry.outputs.loginServer
    // Canonical env vars (build-contract §6) — injected into every container
    cosmosEndpoint: cosmosDb.outputs.endpoint
    postgresHost: postgres.outputs.fqdn
    aiSearchEndpoint: aiSearch.outputs.endpoint
    docIntelEndpoint: documentIntelligence.outputs.endpoint
    contentSafetyEndpoint: contentSafety.outputs.endpoint
    aiFoundryProjectEndpoint: aiFoundry.outputs.projectEndpoint
    openAiEndpoint: aiServices.outputs.openAiEndpoint
    keyVaultEndpoint: keyVault.outputs.endpoint
    tags: tags
  }
}

// ─── Outputs (azd canonical env vars — build-contract §6) ────────────────────
// These are surfaced as environment variables in each container app by azd.
// NO secrets, NO keys, NO connection strings with credentials.

// ── Cosmos DB ────────────────────────────────────────────────────────────────
@description('Cosmos DB account endpoint. Auth: UAMI via DefaultAzureCredential.')
output COSMOS_ENDPOINT string = cosmosDb.outputs.endpoint

@description('Cosmos DB database name.')
output COSMOS_DATABASE string = 'zava'

// ── PostgreSQL ────────────────────────────────────────────────────────────────
@description('PostgreSQL server FQDN.')
output POSTGRES_HOST string = postgres.outputs.fqdn

@description('PostgreSQL database name.')
output POSTGRES_DB string = 'zava'

@description('PostgreSQL port.')
output POSTGRES_PORT string = '5432'

// ── Azure AI Search ───────────────────────────────────────────────────────────
@description('AI Search service endpoint.')
output AZURE_SEARCH_ENDPOINT string = aiSearch.outputs.endpoint

@description('AI Search index name (zava-knowledge).')
output AZURE_SEARCH_INDEX string = 'zava-knowledge'

// ── AI Services ──────────────────────────────────────────────────────────────
@description('Document Intelligence endpoint.')
output AZURE_DOCINTEL_ENDPOINT string = documentIntelligence.outputs.endpoint

@description('Content Safety endpoint.')
output AZURE_CONTENTSAFETY_ENDPOINT string = contentSafety.outputs.endpoint

@description('AI Foundry Project endpoint for AIProjectClient (azure-ai-projects SDK).')
output AZURE_AI_FOUNDRY_PROJECT_ENDPOINT string = aiFoundry.outputs.projectEndpoint

@description('Azure OpenAI endpoint (openai.azure.com format) for Azure OpenAI SDK.')
output AZURE_OPENAI_ENDPOINT string = aiServices.outputs.openAiEndpoint

// ── Platform ──────────────────────────────────────────────────────────────────
@description('Key Vault endpoint (https://...).')
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.endpoint

@description('Application Insights connection string for OpenTelemetry exporters.')
output APPLICATIONINSIGHTS_CONNECTION_STRING string = monitoring.outputs.appInsightsConnectionString

@description('Client ID of the user-assigned managed identity. Set as AZURE_CLIENT_ID in container apps so DefaultAzureCredential targets the UAMI.')
output AZURE_CLIENT_ID string = identity.outputs.clientId

// ── Container App URLs (informational) ───────────────────────────────────────
output API_PYTHON_URL string = containerApps.outputs.apiPythonUrl
output API_DOTNET_URL string = containerApps.outputs.apiDotnetUrl
output MCP_ZAVA_URL string = containerApps.outputs.mcpZavaUrl
