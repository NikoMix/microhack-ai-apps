// ─────────────────────────────────────────────────────────────────────────────
// Module: cosmosDb.bicep
// Provisions Azure Cosmos DB NoSQL account with database 'zava' and containers:
//   - products  (partition key: /id)
//   - orders    (partition key: /customer)
//   - customers (partition key: /id)
//
// Security (build-contract hard requirements):
//   - disableLocalAuthentication: true   ← no connection strings with keys
//   - AAD RBAC data-plane access only    ← via sqlRoleAssignments
//   - disableKeyBasedMetadataWriteAccess: true
//
// The UAMI gets Cosmos DB Built-in Data Contributor (ID: 00000000-...0002)
// which allows CRUD on all databases/containers in the account.
// ─────────────────────────────────────────────────────────────────────────────

@description('Cosmos DB account name.')
param name string

@description('Azure region.')
param location string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Resource tags.')
param tags object = {}

// ── AVM: Cosmos DB Account (NoSQL API) ────────────────────────────────────────
module cosmosAccount 'br/public:avm/res/document-db/database-account:0.19.0' = {
  name: 'cosmosAccount'
  params: {
    name: name
    location: location
    // Use failoverLocations for geo-replication config (replaces deprecated 'locations')
    failoverLocations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    // Build-contract: disable key auth, use AAD RBAC only
    disableLocalAuthentication: true
    disableKeyBasedMetadataWriteAccess: true
    // Assign Cosmos DB Built-in Data Contributor (00000000-0000-0000-0000-000000000002)
    // to the UAMI so it can read/write all documents without a connection string key
    sqlRoleAssignments: [
      {
        principalId: managedIdentityPrincipalId
        roleDefinitionId: '00000000-0000-0000-0000-000000000002'
      }
    ]
    // Cosmos DB SQL database 'zava' with three containers
    sqlDatabases: [
      {
        name: 'zava'
        throughput: 400
        containers: [
          {
            name: 'products'
            paths: ['/id']
          }
          {
            name: 'orders'
            paths: ['/customer']
          }
          {
            name: 'customers'
            paths: ['/id']
          }
        ]
      }
    ]
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('Cosmos DB endpoint — set as COSMOS_ENDPOINT. No key needed (RBAC auth).')
output endpoint string = cosmosAccount.outputs.endpoint

output resourceId string = cosmosAccount.outputs.resourceId
output name string = cosmosAccount.outputs.name
