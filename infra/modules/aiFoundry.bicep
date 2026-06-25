// ─────────────────────────────────────────────────────────────────────────────
// Module: aiFoundry.bicep
// Provisions Azure AI Foundry Hub + Project using the ML Services workspace AVM.
//
// Architecture:
//   Hub  = Microsoft.MachineLearningServices/workspaces (kind: Hub)
//          Shared infrastructure: Storage, Key Vault, App Insights, ACR
//   Project = Microsoft.MachineLearningServices/workspaces (kind: Project)
//             Linked to Hub; isolates per-use-case experiments and deployments
//
// The Hub is connected to the AI Services account (GPT-4o-mini + embeddings).
// Apps use AIProjectClient with AZURE_AI_FOUNDRY_PROJECT_ENDPOINT.
//
// Security:
//   - managedIdentities: systemAssigned — Hub has its own system MI
//   - managedNetworkSettings: Disabled — lab simplicity; use AllowOnlyApprovedOutbound for prod
//   - publicNetworkAccess: Enabled — lab; add private endpoint for prod
// ─────────────────────────────────────────────────────────────────────────────

@description('AI Foundry Hub workspace name.')
param hubName string

@description('AI Foundry Project workspace name.')
param projectName string

@description('Azure region.')
param location string

@description('Resource ID of the Storage Account for workspace artifacts.')
param storageAccountResourceId string

@description('Resource ID of the Key Vault.')
param keyVaultResourceId string

@description('Resource ID of Application Insights.')
param appInsightsResourceId string

@description('Resource ID of Azure Container Registry.')
param containerRegistryResourceId string

@description('Resource ID of the AI Services account (for Hub connection).')
param aiServicesResourceId string

@description('Endpoint of the AI Services account.')
param aiServicesEndpoint string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// Azure AI Developer role: use AI Foundry resources (projects, agents, etc.)
var azureAiDeveloperRoleId = '64702f94-c441-49e6-a78b-ef80e0188fee'

// ── AVM: AI Foundry Hub ────────────────────────────────────────────────────────
module aiHub 'br/public:avm/res/machine-learning-services/workspace:0.13.2' = {
  name: 'aiHub'
  params: {
    name: hubName
    location: location
    // kind: Hub differentiates from classic ML workspace
    kind: 'Hub'
    sku: 'Basic'
    // Shared infrastructure for all projects under this Hub
    associatedStorageAccountResourceId: storageAccountResourceId
    associatedKeyVaultResourceId: keyVaultResourceId
    associatedApplicationInsightsResourceId: appInsightsResourceId
    associatedContainerRegistryResourceId: containerRegistryResourceId
    // Hub has its own system-assigned MI for artifact management
    managedIdentities: {
      systemAssigned: true
    }
    // For lab: no network isolation. For production: 'AllowOnlyApprovedOutbound'
    managedNetworkSettings: {
      isolationMode: 'Disabled'
    }
    publicNetworkAccess: 'Enabled'
    // Grant UAMI Azure AI Developer role on the Hub
    roleAssignments: [
      {
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: azureAiDeveloperRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI has Azure AI Developer access to Foundry Hub'
      }
    ]
    tags: tags
  }
}

// ── AVM: AI Foundry Project ────────────────────────────────────────────────────
// kind: Project links to the Hub and inherits its shared infrastructure.
// hubResourceId is REQUIRED for Project kind.
module aiProject 'br/public:avm/res/machine-learning-services/workspace:0.13.2' = {
  name: 'aiProject'
  params: {
    name: projectName
    location: location
    kind: 'Project'
    sku: 'Basic'
    // Link to parent Hub — Project inherits storage, KV, App Insights, ACR
    hubResourceId: aiHub.outputs.resourceId
    managedIdentities: {
      systemAssigned: true
    }
    publicNetworkAccess: 'Enabled'
    // Grant UAMI Azure AI Developer role on the Project too
    roleAssignments: [
      {
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: azureAiDeveloperRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI has Azure AI Developer access to Foundry Project'
      }
    ]
    tags: tags
  }
}

// ── AI Services Connection from Hub ──────────────────────────────────────────
// Register the AI Services account as a workspace connection so the Hub can
// use GPT-4o-mini and text-embedding-3-small via managed identity.
resource hubAiServicesConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-10-01' = {
  name: '${hubName}/aiservices-connection'
  dependsOn: [aiHub]
  properties: {
    category: 'AIServices'
    target: aiServicesEndpoint
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: aiServicesResourceId
    }
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
output hubResourceId string = aiHub.outputs.resourceId
output hubName string = aiHub.outputs.name
output projectResourceId string = aiProject.outputs.resourceId
output projectName string = aiProject.outputs.name

@description('AI Foundry Project endpoint for AIProjectClient. Format: https://<aiservices-name>.services.ai.azure.com/api/projects/<project-name>')
output projectEndpoint string = '${replace(aiServicesEndpoint, 'cognitiveservices.azure.com/', 'services.ai.azure.com')}/api/projects/${projectName}'
