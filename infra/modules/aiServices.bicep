// ─────────────────────────────────────────────────────────────────────────────
// Module: aiServices.bicep
// Provisions an Azure AI Services (multi-service) Cognitive Services account
// with model deployments for:
//   - gpt-4o-mini (chat completions — INFERENCE_PROVIDER=azure-openai|foundry)
//   - text-embedding-3-small @ 1536 dims (EMBEDDINGS_PROVIDER=azure-openai|foundry)
//
// Security:
//   - disableLocalAuth: true  ← no API keys; managed identity only
//   - Roles granted to UAMI: Cognitive Services OpenAI User + Cognitive Services User
//
// The AIServices kind provides unified endpoints:
//   OpenAI API:   https://<name>.openai.azure.com/
//   Cognitive:    https://<name>.cognitiveservices.azure.com/
//   AI Foundry:   https://<name>.services.ai.azure.com
// ─────────────────────────────────────────────────────────────────────────────

@description('AI Services account name.')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// Cognitive Services OpenAI User: call OpenAI endpoints (chat, embeddings, etc.)
var cogOpenAiUserRoleId = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
// Cognitive Services User: call non-OpenAI Cognitive Services APIs
var cogServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

// ── AVM: Cognitive Services / AI Services account ────────────────────────────
module aiServicesAccount 'br/public:avm/res/cognitive-services/account:0.15.0' = {
  name: 'aiServicesAccount'
  params: {
    name: name
    location: location
    // AIServices kind: bundles OpenAI, Language, Vision, Speech under one endpoint
    kind: 'AIServices'
    sku: 'S0'
    customSubDomainName: name
    // Disable local auth — DefaultAzureCredential / UAMI only
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    // Model deployments (GPT-4o-mini for chat; text-embedding-3-small for RAG)
    deployments: [
      {
        name: 'gpt-4o-mini'
        model: {
          format: 'OpenAI'
          name: 'gpt-4o-mini'
          version: '2024-07-18'
        }
        sku: {
          name: 'GlobalStandard'
          capacity: 10
        }
        raiPolicyName: 'Microsoft.Default'
        versionUpgradeOption: 'OnceCurrentVersionExpired'
      }
      {
        name: 'text-embedding-3-small'
        model: {
          format: 'OpenAI'
          name: 'text-embedding-3-small'
          version: '1'
        }
        sku: {
          name: 'GlobalStandard'
          capacity: 10
        }
        raiPolicyName: 'Microsoft.Default'
        versionUpgradeOption: 'OnceCurrentVersionExpired'
      }
    ]
    roleAssignments: [
      {
        // OpenAI chat + embedding calls
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: cogOpenAiUserRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI calls OpenAI endpoints (chat, embeddings)'
      }
      {
        // General Cognitive Services API calls
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: cogServicesUserRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI calls Cognitive Services APIs'
      }
    ]
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('Cognitive Services endpoint (https://<name>.cognitiveservices.azure.com).')
output endpoint string = aiServicesAccount.outputs.endpoint

@description('OpenAI-compatible endpoint (https://<name>.openai.azure.com) — set as AZURE_OPENAI_ENDPOINT.')
output openAiEndpoint string = 'https://${name}.openai.azure.com/'

@description('AI Foundry base URL — used to construct AZURE_AI_FOUNDRY_PROJECT_ENDPOINT.')
output aiFoundryBaseUrl string = 'https://${name}.services.ai.azure.com'

output resourceId string = aiServicesAccount.outputs.resourceId
output name string = aiServicesAccount.outputs.name
