targetScope = 'subscription'

@description('The name of the resource group')
param resourceGroupName string = 'rg-secret-santa'

@description('The location for all resources')
param location string = 'australiaeast'

@description('The name of the application')
param appName string = 'secret-santa'

@description('The SKU for the App Service Plan')
param appServicePlanSku string = 'B1'

@description('Python version for the App Service')
@allowed(['3.9', '3.10', '3.11', '3.12'])
param pythonVersion string = '3.11'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: resourceGroupName
  location: location
  properties: {}
}

module mainModule 'main.bicep' = {
  name: 'mainModule'
  scope: resourceGroup
  params: {
    appName: appName
    location: location
    appServicePlanSku: appServicePlanSku
    pythonVersion: pythonVersion
  }
}

output appServiceName string = mainModule.outputs.appServiceName
output appServiceUrl string = mainModule.outputs.appServiceUrl

