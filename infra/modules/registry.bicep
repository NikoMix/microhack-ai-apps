// ─────────────────────────────────────────────────────────────────────────────
// Module: registry.bicep
// Provisions Azure Container Registry (ACR) for storing Docker images.
//
// Security:
//   - adminUserEnabled: false          ← no admin credentials
//   - anonymousPullEnabled: false      ← build-contract hard requirement
//   - publicNetworkAccess: Enabled     ← lab; add private endpoint for prod
//
// Grants the UAMI 'AcrPull' so Container Apps can pull images without a password.
// ─────────────────────────────────────────────────────────────────────────────

@description('ACR name (5–50 lowercase alphanumeric, no hyphens).')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// AcrPull (built-in): pull container images from ACR
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

// ── AVM: Container Registry ───────────────────────────────────────────────────
module acr 'br/public:avm/res/container-registry/registry:0.12.1' = {
  name: 'acr'
  params: {
    name: name
    location: location
    acrSku: 'Basic'
    // Build-contract hard requirements:
    acrAdminUserEnabled: false
    anonymousPullEnabled: false
    publicNetworkAccess: 'Enabled'
    // Grant UAMI AcrPull so Container Apps authenticate to ACR via managed identity
    roleAssignments: [
      {
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: acrPullRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI pulls images without admin credentials'
      }
    ]
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('ACR login server (e.g. crxxx.azurecr.io).')
output loginServer string = acr.outputs.loginServer

output resourceId string = acr.outputs.resourceId
output name string = acr.outputs.name
