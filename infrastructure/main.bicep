@description('The name of the application')
param appName string = 'secret-santa'

@description('The location for all resources')
param location string = resourceGroup().location

@description('The SKU for the App Service Plan')
param appServicePlanSku string = 'B1'

@description('Python version for the App Service')
@allowed(['3.9', '3.10', '3.11', '3.12'])
param pythonVersion string = '3.11'

var uniqueSuffix = uniqueString(resourceGroup().id)
var appServicePlanName = '${appName}-plan-${uniqueSuffix}'
var appServiceName = '${appName}-app-${uniqueSuffix}'

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: appServicePlanSku
    tier: 'Basic'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
  tags: {
    application: appName
    environment: 'production'
  }
}

resource appService 'Microsoft.Web/sites@2023-12-01' = {
  name: appServiceName
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|${pythonVersion}'
      appCommandLine: 'gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 120 web:app'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        {
          name: 'POST_BUILD_COMMAND'
          value: 'pip install -r requirements.txt'
        }
        {
          name: 'WEBSITE_HTTPLOGGING_RETENTION_DAYS'
          value: '7'
        }
      ]
      alwaysOn: true
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
    clientAffinityEnabled: false
  }
  tags: {
    application: appName
    environment: 'production'
  }
}

output appServiceName string = appService.name
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
output appServicePlanName string = appServicePlan.name

