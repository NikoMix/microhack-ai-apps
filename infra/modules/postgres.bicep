// ─────────────────────────────────────────────────────────────────────────────
// Module: postgres.bicep
// Provisions Azure Database for PostgreSQL Flexible Server.
//
// Configuration:
//   - Database: zava (created via 'databases' parameter)
//   - Extension: vector (pgvector) allowlisted in server configuration
//     → Apps run `CREATE EXTENSION IF NOT EXISTS vector;` at startup
//   - Embedding dimension: 1536 (matches text-embedding-3-small)
//
// Security:
//   - authConfig.passwordAuth: Disabled  ← no password connections
//   - authConfig.activeDirectoryAuth: Enabled  ← AAD / managed identity only
//   - UAMI registered as AAD admin
//   - administratorLoginPassword required only during initial provisioning
//     (Bicep management plane); never used by the application
//
// For production: add VNet integration, private DNS zone, disable public access.
// ─────────────────────────────────────────────────────────────────────────────

@description('PostgreSQL Flexible Server name.')
param name string

@description('Azure region.')
param location string

@description('PostgreSQL admin login (management plane only; app uses AAD).')
param administratorLogin string

@secure()
@description('PostgreSQL admin password (used only during provisioning; password auth is disabled afterwards).')
param administratorLoginPassword string

@description('Principal ID of the user-assigned managed identity (added as AAD admin).')
param managedIdentityPrincipalId string

@description('Name of the user-assigned managed identity (used as PostgreSQL AAD admin name).')
param managedIdentityName string

@description('Resource tags.')
param tags object = {}

// ── AVM: PostgreSQL Flexible Server ──────────────────────────────────────────
module postgresServer 'br/public:avm/res/db-for-postgre-sql/flexible-server:0.15.4' = {
  name: 'postgresServer'
  params: {
    name: name
    location: location
    // Burstable tier for cost-effective training lab deployment
    skuName: 'Standard_B2ms'
    tier: 'Burstable'
    storageSizeGB: 32
    // PostgreSQL 16 with pgvector support
    version: '16'
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    // AAD auth enabled; password auth disabled
    // The app connects via managed identity token (DefaultAzureCredential)
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'
      tenantId: tenant().tenantId
    }
    // Register UAMI as PostgreSQL AAD admin
    administrators: [
      {
        principalType: 'ServicePrincipal'
        principalName: managedIdentityName
        objectId: managedIdentityPrincipalId
        tenantId: tenant().tenantId
      }
    ]
    // Create the 'zava' database
    databases: [
      {
        name: 'zava'
        charset: 'UTF8'
        collation: 'en_US.utf8'
      }
    ]
    // Allowlist pgvector extension so apps can run: CREATE EXTENSION IF NOT EXISTS vector;
    configurations: [
      {
        name: 'azure.extensions'
        value: 'vector'
      }
    ]
    // Allow Azure services (e.g., Container Apps) to connect
    firewallRules: [
      {
        name: 'AllowAzureServices'
        startIpAddress: '0.0.0.0'
        endIpAddress: '0.0.0.0'
      }
    ]
    // No HA for training lab (reduces cost)
    highAvailability: 'Disabled'
    // availabilityZone is required by the module even when HA is disabled
    availabilityZone: 1
    // No geo-redundant backup for training lab
    backupRetentionDays: 7
    geoRedundantBackup: 'Disabled'
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
@description('PostgreSQL server FQDN — set as POSTGRES_HOST.')
output fqdn string = postgresServer.outputs.?fqdn ?? ''

output resourceId string = postgresServer.outputs.resourceId
output name string = postgresServer.outputs.name
