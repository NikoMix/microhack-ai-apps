// ─────────────────────────────────────────────────────────────────────────────
// Module: identity.bicep
// Provisions a single User-Assigned Managed Identity for the Zava platform.
// All Container Apps use this UAMI for DefaultAzureCredential / Managed Identity
// auth to every data and AI service — NO API keys ever leave Key Vault.
// ─────────────────────────────────────────────────────────────────────────────

@description('Name for the user-assigned managed identity.')
param name string

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

// ── AVM: User-Assigned Managed Identity ──────────────────────────────────────
module uami 'br/public:avm/res/managed-identity/user-assigned-identity:0.5.1' = {
  name: 'uami'
  params: {
    name: name
    location: location
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('Resource ID of the managed identity.')
output resourceId string = uami.outputs.resourceId

@description('Principal (object) ID — used in RBAC role assignments.')
output principalId string = uami.outputs.principalId

@description('Client ID — set as AZURE_CLIENT_ID env var so apps use DefaultAzureCredential.')
output clientId string = uami.outputs.clientId

@description('Resource name.')
output name string = uami.outputs.name
