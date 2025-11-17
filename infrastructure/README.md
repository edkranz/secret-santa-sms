# Azure Infrastructure Deployment

This directory contains Bicep templates for deploying the Secret Santa application to Azure.

## Prerequisites

- Azure CLI installed and configured
- Azure subscription with appropriate permissions
- GitHub repository with secrets configured (see below)

## GitHub Secrets Required

Configure the following secrets in your GitHub repository:

1. **AZURE_CREDENTIALS** - Service principal credentials in JSON format:
   ```json
  {
    "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "clientSecret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "subscriptionId": "8fe27bea-9457-4b6e-850b-618b322fe2cf",
    "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
   ```

2. **AZURE_SUBSCRIPTION_ID** - Your Azure subscription ID

3. **AZURE_RG_NAME** - Name of the resource group (e.g., `rg-secret-santa`)

4. **AZURE_COMMUNICATION_CONNECTION_STRING** - Azure Communication Services connection string

5. **AZURE_SENDER_EMAIL** - Verified sender email address for Azure Communication Services

## Manual Deployment

To deploy manually using Azure CLI:

```bash
# Login to Azure
az login

# Create resource group (if it doesn't exist)
az group create --name rg-secret-santa --location australiaeast

# Deploy infrastructure
az deployment sub create \
  --location australiaeast \
  --template-file infrastructure/azuredeploy.bicep \
  --parameters resourceGroupName=rg-secret-santa appName=secret-santa
```

## Architecture

The infrastructure deploys:

- **App Service Plan** (Linux, Basic tier)
- **App Service** (Python 3.11)
  - Configured for HTTPS only
  - Always On enabled
  - Build automation enabled

## Environment Variables

The following environment variables are set via GitHub Actions:

- `AZURE_COMMUNICATION_CONNECTION_STRING` - From GitHub secrets
- `AZURE_SENDER_EMAIL` - From GitHub secrets
- `EMAIL_TEMPLATE_PATH` - Set to `email_template.html`

