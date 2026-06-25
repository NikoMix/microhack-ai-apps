// ─────────────────────────────────────────────────────────────────────────────
// Module: aiSearch.bicep
// Provisions Azure AI Search for the RAG knowledge base (Zava policies,
// product catalog, reviews). Used by the `concierge` and `merchandiser` agents.
//
// Index name: zava-knowledge (AZURE_SEARCH_INDEX canonical env var)
// Embedding dimension: 1536 (text-embedding-3-small)
//
// Security:
//   - disableLocalAuth: true  ← no API keys; managed identity only
//   - Roles granted to UAMI: Search Index Data Contributor + Search Service Contributor
// ─────────────────────────────────────────────────────────────────────────────

@description('AI Search service name.')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// Search Index Data Contributor: read/write search index data
var searchIndexDataContributorRoleId = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
// Search Service Contributor: manage search service (create indexes, etc.)
var searchServiceContributorRoleId = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'

// ── AVM: Azure AI Search ──────────────────────────────────────────────────────
module search 'br/public:avm/res/search/search-service:0.12.2' = {
  name: 'search'
  params: {
    name: name
    location: location
    sku: 'basic'
    replicaCount: 1
    partitionCount: 1
    // Disable local API keys — only AAD / managed identity auth
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    roleAssignments: [
      {
        // Index data CRUD (ingest documents, run queries)
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: searchIndexDataContributorRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI reads/writes search index data'
      }
      {
        // Management plane (create/update index schema, etc.)
        principalId: managedIdentityPrincipalId
        roleDefinitionIdOrName: searchServiceContributorRoleId
        principalType: 'ServicePrincipal'
        description: 'UAMI manages search indexes'
      }
    ]
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('AI Search endpoint — set as AZURE_SEARCH_ENDPOINT.')
output endpoint string = 'https://${name}.search.windows.net'

output resourceId string = search.outputs.resourceId
output name string = search.outputs.name
