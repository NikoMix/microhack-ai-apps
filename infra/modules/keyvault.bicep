// ─────────────────────────────────────────────────────────────────────────────
// Module: keyvault.bicep
// Provisions Azure Key Vault with RBAC authorization model (no access policies).
//
// Security:
//   - enableRbacAuthorization: true   ← RBAC mode (access policies disabled)
//   - enablePurgeProtection: true     ← build-contract hard requirement
//   - enableSoftDelete: true          ← 90-day retention
//   - publicNetworkAccess: Enabled    ← lab simplicity; add private endpoint for prod
//
// Grants the UAMI 'Key Vault Secrets User' so Container Apps can read secrets.
// ─────────────────────────────────────────────────────────────────────────────

@description('Key Vault name (3–24 alphanumeric + hyphens).')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// Key Vault Secrets User (built-in): read secret values
var kvSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'

// ── AVM: Key Vault ────────────────────────────────────────────────────────────
module kv 'br/public:avm/res/key-vault/vault:0.13.3' = {
  name: 'kv'
  params: {
    name: name
    location: location
    // RBAC authorization — access policies are deprecated
    enableRbacAuthorization: true
    // Build-contract hard requirement: purge protection ON
    enablePurgeProtection: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    // Enable for lab access; restrict with private endpoint + network ACLs for production
    publicNetworkAccess: 'Enabled'
    // Grant UAMI read access to secrets (e.g., PG admin password during bootstrapping)
    roleAssignments: [
      {
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: kvSecretsUserRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI reads secrets via DefaultAzureCredential'
      }
    ]
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('Key Vault endpoint — set as AZURE_KEY_VAULT_ENDPOINT env var.')
output endpoint string = kv.outputs.uri

output resourceId string = kv.outputs.resourceId
output name string = kv.outputs.name
