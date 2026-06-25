// ─────────────────────────────────────────────────────────────────────────────
// Module: documentIntelligence.bicep
// Provisions Azure AI Document Intelligence (formerly Form Recognizer).
// Used by the `operations` agent to parse supplier documents.
//
// Security: disableLocalAuth: true — UAMI only via DefaultAzureCredential.
// ─────────────────────────────────────────────────────────────────────────────

@description('Document Intelligence account name.')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// Cognitive Services User: call Document Intelligence APIs
var cogServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

// ── AVM: Document Intelligence (kind: FormRecognizer) ────────────────────────
// NOTE: The Bicep kind value is 'FormRecognizer' even though the portal shows
// 'Document Intelligence'. This is the correct API kind string.
module docIntel 'br/public:avm/res/cognitive-services/account:0.15.0' = {
  name: 'docIntel'
  params: {
    name: name
    location: location
    kind: 'FormRecognizer'
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
        description: 'UAMI calls Document Intelligence APIs'
      }
    ]
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('Document Intelligence endpoint — set as AZURE_DOCINTEL_ENDPOINT.')
output endpoint string = docIntel.outputs.endpoint

output resourceId string = docIntel.outputs.resourceId
output name string = docIntel.outputs.name
