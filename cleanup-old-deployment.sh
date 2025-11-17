#!/bin/bash

# Cleanup script for old Azure deployments
# Run this if you're getting "Conflict" errors due to existing resources

set -e

echo "🔍 Azure Deployment Cleanup Script"
echo "===================================="
echo ""

# Check if user is logged in
if ! az account show &>/dev/null; then
    echo "❌ Not logged into Azure. Please run: az login"
    exit 1
fi

echo "✅ Logged into Azure"
echo ""

# Get current subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
echo "📋 Current subscription: $SUBSCRIPTION"
echo ""

# Prompt for resource group name
read -p "Enter your resource group name (from AZURE_RG_NAME secret): " RG_NAME

if [ -z "$RG_NAME" ]; then
    echo "❌ Resource group name cannot be empty"
    exit 1
fi

echo ""
echo "🔍 Checking for resource group: $RG_NAME"

# Check if resource group exists
if az group show --name "$RG_NAME" &>/dev/null; then
    echo "✅ Resource group exists"
    echo ""
    
    # List all resources in the resource group
    echo "📦 Resources in $RG_NAME:"
    az resource list --resource-group "$RG_NAME" --query "[].{Name:name, Type:type, Location:location}" -o table
    echo ""
    
    # Ask if user wants to delete everything
    read -p "⚠️  Do you want to DELETE the entire resource group and start fresh? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" = "yes" ]; then
        echo ""
        echo "🗑️  Deleting resource group $RG_NAME..."
        az group delete --name "$RG_NAME" --yes --no-wait
        echo ""
        echo "✅ Deletion initiated (running in background)"
        echo "⏳ Wait 2-3 minutes before re-running your GitHub Actions deployment"
        echo ""
        echo "To check deletion status:"
        echo "  az group show --name $RG_NAME"
        echo ""
    else
        echo ""
        echo "❌ Deletion cancelled"
        echo ""
        echo "🔧 Alternative solutions:"
        echo ""
        echo "1. Check for conflicting App Service names:"
        echo "   az webapp list --query \"[?name=='secret-santa-app' || contains(name, 'secret-santa')].{Name:name, RG:resourceGroup, State:state}\" -o table"
        echo ""
        echo "2. Delete just the App Service and Plan:"
        echo "   az webapp delete --name secret-santa-app --resource-group $RG_NAME"
        echo "   az appservice plan delete --name secret-santa-plan --resource-group $RG_NAME --yes"
        echo ""
        echo "3. Check deployment status:"
        echo "   az deployment sub list --query \"[?contains(name, 'secret-santa')].{Name:name, State:properties.provisioningState, Timestamp:properties.timestamp}\" -o table"
        echo ""
    fi
else
    echo "✅ Resource group does not exist (this is fine for first deployment)"
    echo "🚀 You can proceed with the deployment"
fi

echo ""
echo "Done!"

