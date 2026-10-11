// ─────────────────────────────────────────────────────────────────────────────
// Module: monitoring.bicep
// Provisions Log Analytics Workspace + workspace-based Application Insights.
// Classic App Insights is DEPRECATED — always use workspace-based.
// All Container Apps send OpenTelemetry telemetry to Application Insights.
// ─────────────────────────────────────────────────────────────────────────────

@description('Name for the Log Analytics workspace.')
param logAnalyticsName string

@description('Name for the Application Insights component.')
param appInsightsName string

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

// ── AVM: Log Analytics Workspace ─────────────────────────────────────────────
// Deploy first — App Insights and Container Apps Environment depend on it.
module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.15.1' = {
  name: 'logAnalytics'
  params: {
    name: logAnalyticsName
    location: location
    skuName: 'PerGB2018'
    dataRetention: 90
    tags: tags
  }
}

// ── AVM: Application Insights (workspace-based) ───────────────────────────────
// workspaceResourceId wires App Insights to Log Analytics for unified querying.
module appInsights 'br/public:avm/res/insights/component:0.7.2' = {
  name: 'appInsights'
  params: {
    name: appInsightsName
    location: location
    workspaceResourceId: logAnalytics.outputs.resourceId
    applicationType: 'web'
    kind: 'web'
    tags: tags
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
output logAnalyticsWorkspaceResourceId string = logAnalytics.outputs.resourceId
output logAnalyticsWorkspaceId string = logAnalytics.outputs.logAnalyticsWorkspaceId

@description('Connection string used by OpenTelemetry exporters and APPLICATIONINSIGHTS_CONNECTION_STRING env var.')
output appInsightsConnectionString string = appInsights.outputs.connectionString

output appInsightsResourceId string = appInsights.outputs.resourceId
output appInsightsInstrumentationKey string = appInsights.outputs.instrumentationKey
