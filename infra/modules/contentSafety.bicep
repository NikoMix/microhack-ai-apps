// ─────────────────────────────────────────────────────────────────────────────
// Module: contentSafety.bicep
// Provisions Azure AI Content Safety.
// Used by the `trust` agent to evaluate responses for harmful content.
//
// Security: disableLocalAuth: true — UAMI only via DefaultAzureCredential.
// ─────────────────────────────────────────────────────────────────────────────

@description('Content Safety account name.')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// Cognitive Services User: call Content Safety APIs
var cogServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

// ── AVM: Content Safety ───────────────────────────────────────────────────────
module contentSafety 'br/public:avm/res/cognitive-services/account:0.15.0' = {
  name: 'contentSafety'
  params: {
    name: name
    location: location
    kind: 'ContentSafety'
    sku: 'S0'
    customSubDomainName: name
    // Disable local auth — managed identity only
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    roleAssignments: [
      {
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: cogServicesUserRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI calls Content Safety APIs'
      }
    ]
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('Content Safety endpoint — set as AZURE_CONTENTSAFETY_ENDPOINT.')
output endpoint string = contentSafety.outputs.endpoint

output resourceId string = contentSafety.outputs.resourceId
output name string = contentSafety.outputs.name
