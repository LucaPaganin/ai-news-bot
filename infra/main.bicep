// main.bicep
param environmentName string
param location string = resourceGroup().location
param TELEGRAM_API_TOKEN string
param CHAT_ID string

var prefix = 'ainewsbot'
var uniqueSuffix = toLower(uniqueString(resourceGroup().id))

var appServicePlanName = '${prefix}-asp-${environmentName}-${uniqueSuffix}'
var webAppName = '${prefix}-web-${environmentName}-${uniqueSuffix}'
var appInsightsName = '${prefix}-appi-${environmentName}-${uniqueSuffix}'
var logAnalyticsName = '${prefix}-log-${environmentName}-${uniqueSuffix}'

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'F1'
    tier: 'Free'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'TELEGRAM_API_TOKEN'
          value: TELEGRAM_API_TOKEN
        }
        {
          name: 'CHAT_ID'
          value: CHAT_ID
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
      ]
    }
  }
  dependsOn: [appServicePlan, appInsights]
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

output webAppName string = webApp.name
output appServicePlanName string = appServicePlan.name
output appInsightsName string = appInsights.name
output logAnalyticsName string = logAnalytics.name
