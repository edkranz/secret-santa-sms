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
     "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
     "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
   }
   ```
   
   To create a service principal:
   ```bash
   az ad sp create-for-rbac --name "secret-santa-deploy" \
     --role contributor \
     --scopes /subscriptions/{subscription-id} \
     --sdk-auth
   ```

2. **AZURE_SUBSCRIPTION_ID** - Your Azure subscription ID

3. **AZURE_RG_NAME** - Name of the resource group (e.g., `rg-secret-santa`)

4. **AZURE_COMMUNICATION_CONNECTION_STRING** - Azure Communication Services connection string

5. **AZURE_SENDER_EMAIL** - Verified sender email address for Azure Communication Services

6. **RECAPTCHA_SECRET_KEY** - Google reCAPTCHA v2 secret key for bot protection (RECOMMENDED)

7. **RECAPTCHA_SITE_KEY** - Google reCAPTCHA v2 site key for bot protection (RECOMMENDED)
   ```bash
   # Get keys from: https://www.google.com/recaptcha/admin/create
   # See RECAPTCHA_SETUP.md for detailed instructions
   
   gh secret set RECAPTCHA_SECRET_KEY --body 'your-secret-key'
   gh secret set RECAPTCHA_SITE_KEY --body 'your-site-key'
   ```

## Manual Deployment

To deploy manually using Azure CLI:

```bash
# Login to Azure
az login

# Deploy infrastructure (resource group is created automatically)
az deployment sub create \
  --location australiaeast \
  --template-file infrastructure/azuredeploy.bicep \
  --parameters \
    resourceGroupName=rg-secret-santa \
    appName=secret-santa \
    location=australiaeast \
    pythonVersion=3.11
```

## Architecture

The infrastructure deploys:

- **Resource Group** - Container for all resources
- **App Service Plan** (Linux, Basic B1 tier)
  - Name: `{appName}-plan-{uniqueSuffix}` (e.g., `secret-santa-plan-abc123xyz`)
  - 1.75 GB RAM, 1 vCPU
  - Reserved for Linux containers
- **App Service** (Python 3.11)
  - Name: `{appName}-app-{uniqueSuffix}` (e.g., `secret-santa-app-abc123xyz`)
  - Globally unique name generated using `uniqueString(resourceGroup().id)`
  - HTTPS only enforced
  - Always On enabled
  - FTPS disabled for security
  - TLS 1.2 minimum
  - Build automation with Oryx
  - Gunicorn configured as startup command

**Note:** Resource names include a unique suffix to ensure global uniqueness across Azure.

## Deployment Flow

1. **Infrastructure Deployment** - Creates/updates Azure resources
2. **Configuration** - Sets application settings and secrets
3. **Package Creation** - Zips application files
4. **App Deployment** - Uploads and deploys code to App Service
5. **Restart** - Restarts the app to apply changes

## Environment Variables

The following environment variables are configured via GitHub Actions:

- `AZURE_COMMUNICATION_CONNECTION_STRING` - Azure Communication Services connection string
- `AZURE_SENDER_EMAIL` - Verified sender email address
- `EMAIL_TEMPLATE_PATH` - Path to email template (`email_template.html`)

## Troubleshooting

### Conflict Error

If you see a "Conflict" error, it usually means:
- Resources already exist from a previous deployment with DIFFERENT names
- The old resources need to be cleaned up first

**Solution 1 - Clean up old resources:**
```bash
# Run the cleanup script
chmod +x cleanup-old-deployment.sh
./cleanup-old-deployment.sh
```

**Solution 2 - Manual cleanup:**
```bash
# Delete the entire resource group and redeploy
az group delete --name <your-rg-name> --yes
# Wait 2-3 minutes, then re-run the deployment
```

**Note:** As of the latest fix, all resource names use `uniqueString()` to ensure global uniqueness and prevent conflicts.

### Deployment Failed

Check the deployment logs in Azure Portal:
1. Navigate to Subscriptions → Deployments
2. Find your deployment by name (secret-santa-deployment-{run_number})
3. Review operation details for specific errors

### App Not Starting

Check application logs:
```bash
az webapp log tail --name secret-santa-app --resource-group rg-secret-santa
```

