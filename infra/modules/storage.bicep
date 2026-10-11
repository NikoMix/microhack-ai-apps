// ─────────────────────────────────────────────────────────────────────────────
// Module: storage.bicep
// Provisions the Storage Account required by Azure AI Foundry Hub for workspace
// artifacts (notebooks, datasets, evaluation outputs).
//
// Security:
//   - allowBlobPublicAccess: false
//   - allowSharedKeyAccess: false  ← RBAC only; no storage keys
//   - minimumTlsVersion: TLS1_2
// ─────────────────────────────────────────────────────────────────────────────

@description('Storage account name (3–24 lowercase alphanumeric chars).')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity (granted Storage Blob Data Contributor).')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// Storage Blob Data Contributor role definition ID (built-in)
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

// ── Storage Account (direct resource — no AVM Storage module version pinned) ──
// Using direct resource declaration to avoid registry version uncertainty.
// Storage accounts for AI Foundry must exist before the Hub is provisioned.
resource storageAccount 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: name
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    // Blob public access disabled — no anonymous reads
    allowBlobPublicAccess: false
    // Shared key access disabled — enforce RBAC only (DefaultAzureCredential)
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    // Default OAuth so SDKs use managed identity by default
    defaultToOAuthAuthentication: true
    accessTier: 'Hot'
    encryption: {
      services: {
        blob: { enabled: true, keyType: 'Account' }
        file: { enabled: true, keyType: 'Account' }
      }
      keySource: 'Microsoft.Storage'
    }
  }
  tags: tags
}

// Blob service (enable soft delete for AI Foundry artifact safety)
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

// ── Role: Storage Blob Data Contributor → user-assigned MI ──────────────────
// Required so our Container Apps can read/write AI Foundry artifacts via MI.
resource blobDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, managedIdentityPrincipalId, storageBlobDataContributorRoleId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Allows UAMI to read/write blobs for AI Foundry artifacts'
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
output resourceId string = storageAccount.id
output name string = storageAccount.name
