// ─────────────────────────────────────────────────────────────────────────────
// Module: containerApps.bicep
// Provisions:
//   1. Container Apps Environment (linked to Log Analytics)
//   2. Three Container Apps:
//        - api-python  (FastAPI + agent-framework)
//        - api-dotnet  (.NET Minimal API + Microsoft.Agents.AI)
//        - mcp-zava    (Zava MCP server)
//
// azd integration:
//   Each container app is tagged with `azd-service-name` so azd's deploy phase
//   can find the app, push the Docker image from ACR, and update the container.
//   Placeholder image is used until `azd deploy` runs.
//
// Security:
//   - managedIdentities: user-assigned UAMI — DefaultAzureCredential in app code
//   - ACR pull via UAMI (no admin credentials / password)
//   - All env vars injected from Bicep outputs (no secrets in code)
//   - AZURE_CLIENT_ID enables DefaultAzureCredential to target the UAMI
// ─────────────────────────────────────────────────────────────────────────────

@description('Container Apps Environment name.')
param environmentName string

@description('Azure region.')
param location string

@description('Application Insights connection string (used for environment-level telemetry and injected as env var).')
param appInsightsConnectionString string

@description('Resource ID of the user-assigned managed identity.')
param managedIdentityResourceId string

@description('Client ID of the user-assigned managed identity (AZURE_CLIENT_ID).')
param managedIdentityClientId string

@description('ACR login server (for image pull).')
param acrLoginServer string

// ── Canonical env vars (from azd outputs, per build-contract §6) ─────────────
@description('Cosmos DB endpoint.')
param cosmosEndpoint string

@description('PostgreSQL FQDN.')
param postgresHost string

@description('Azure AI Search endpoint.')
param aiSearchEndpoint string

@description('Document Intelligence endpoint.')
param docIntelEndpoint string

@description('Content Safety endpoint.')
param contentSafetyEndpoint string

@description('AI Foundry Project endpoint.')
param aiFoundryProjectEndpoint string

@description('Azure OpenAI endpoint.')
param openAiEndpoint string

@description('Key Vault endpoint.')
param keyVaultEndpoint string

@description('Resource tags.')
param tags object = {}

// Placeholder image — replaced by azd deploy with the real built image
var placeholderImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

// Common environment variables injected into all container apps.
// Apps consume these via process.env (Python) or IConfiguration (.NET).
// AZURE_CLIENT_ID tells DefaultAzureCredential which UAMI to use.
var commonEnvVars = [
  { name: 'AZURE_CLIENT_ID', value: managedIdentityClientId }
  { name: 'COSMOS_ENDPOINT', value: cosmosEndpoint }
  { name: 'COSMOS_DATABASE', value: 'zava' }
  { name: 'POSTGRES_HOST', value: postgresHost }
  { name: 'POSTGRES_DB', value: 'zava' }
  { name: 'POSTGRES_PORT', value: '5432' }
  { name: 'AZURE_SEARCH_ENDPOINT', value: aiSearchEndpoint }
  { name: 'AZURE_SEARCH_INDEX', value: 'zava-knowledge' }
  { name: 'AZURE_DOCINTEL_ENDPOINT', value: docIntelEndpoint }
  { name: 'AZURE_CONTENTSAFETY_ENDPOINT', value: contentSafetyEndpoint }
  { name: 'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT', value: aiFoundryProjectEndpoint }
  { name: 'AZURE_OPENAI_ENDPOINT', value: openAiEndpoint }
  { name: 'AZURE_OPENAI_CHAT_DEPLOYMENT', value: 'gpt-4o-mini' }
  { name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT', value: 'text-embedding-3-small' }
  { name: 'AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT', value: 'gpt-4o-mini' }
  { name: 'AZURE_KEY_VAULT_ENDPOINT', value: keyVaultEndpoint }
  { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
  { name: 'INFERENCE_PROVIDER', value: 'azure-openai' }
  { name: 'EMBEDDINGS_PROVIDER', value: 'azure-openai' }
]

// ── AVM: Container Apps Environment ──────────────────────────────────────────
module cae 'br/public:avm/res/app/managed-environment:0.13.3' = {
  name: 'cae'
  params: {
    name: environmentName
    location: location
    // Use App Insights for environment-level platform telemetry
    appInsightsConnectionString: appInsightsConnectionString
    // Consumption workload profile (serverless, no dedicated nodes)
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    // Public ingress at environment level (each app controls its own ingress)
    internal: false
    tags: tags
  }
}

// ── AVM: api-python Container App ────────────────────────────────────────────
// FastAPI + Microsoft Agent Framework (Python track)
// Port 8000 (FastAPI default)
module apiPython 'br/public:avm/res/app/container-app:0.22.1' = {
  name: 'apiPython'
  params: {
    name: 'ca-api-python'
    location: location
    environmentResourceId: cae.outputs.resourceId
    // UAMI for DefaultAzureCredential — no passwords or API keys in code
    managedIdentities: {
      userAssignedResourceIds: [managedIdentityResourceId]
    }
    containers: [
      {
        name: 'api-python'
        // Placeholder replaced by `azd deploy` when src/python/Dockerfile is built
        image: placeholderImage
        resources: {
          cpu: any(json('0.5'))
          memory: '1Gi'
        }
        env: commonEnvVars
      }
    ]
    // ACR pull via UAMI identity (no admin username/password)
    registries: [
      {
        server: acrLoginServer
        identity: managedIdentityResourceId
      }
    ]
    ingressExternal: true
    ingressTargetPort: 8000
    ingressTransport: 'auto'
    // azd uses this tag to identify which container app belongs to this service
    tags: union(tags, { 'azd-service-name': 'api-python' })
  }
}

// ── AVM: api-dotnet Container App ─────────────────────────────────────────────
// ASP.NET Core Minimal API + Microsoft.Agents.AI (.NET track)
// Port 8080 (ASP.NET Core default)
module apiDotnet 'br/public:avm/res/app/container-app:0.22.1' = {
  name: 'apiDotnet'
  params: {
    name: 'ca-api-dotnet'
    location: location
    environmentResourceId: cae.outputs.resourceId
    managedIdentities: {
      userAssignedResourceIds: [managedIdentityResourceId]
    }
    containers: [
      {
        name: 'api-dotnet'
        image: placeholderImage
        resources: {
          cpu: any(json('0.5'))
          memory: '1Gi'
        }
        env: commonEnvVars
      }
    ]
    registries: [
      {
        server: acrLoginServer
        identity: managedIdentityResourceId
      }
    ]
    ingressExternal: true
    ingressTargetPort: 8080
    ingressTransport: 'auto'
    tags: union(tags, { 'azd-service-name': 'api-dotnet' })
  }
}

// ── AVM: mcp-zava Container App ───────────────────────────────────────────────
// Zava MCP server (exposes tools to IDE / Copilot via MCP protocol)
// Port 3000 (MCP default)
module mcpZava 'br/public:avm/res/app/container-app:0.22.1' = {
  name: 'mcpZava'
  params: {
    name: 'ca-mcp-zava'
    location: location
    environmentResourceId: cae.outputs.resourceId
    managedIdentities: {
      userAssignedResourceIds: [managedIdentityResourceId]
    }
    containers: [
      {
        name: 'mcp-zava'
        image: placeholderImage
        resources: {
          cpu: any(json('0.25'))
          memory: '0.5Gi'
        }
        env: commonEnvVars
      }
    ]
    registries: [
      {
        server: acrLoginServer
        identity: managedIdentityResourceId
      }
    ]
    ingressExternal: true
    ingressTargetPort: 3000
    ingressTransport: 'auto'
    tags: union(tags, { 'azd-service-name': 'mcp-zava' })
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
output environmentResourceId string = cae.outputs.resourceId
output environmentName string = cae.outputs.name
output environmentDefaultDomain string = cae.outputs.defaultDomain

output apiPythonUrl string = 'https://${apiPython.outputs.fqdn}'
output apiDotnetUrl string = 'https://${apiDotnet.outputs.fqdn}'
output mcpZavaUrl string = 'https://${mcpZava.outputs.fqdn}'
