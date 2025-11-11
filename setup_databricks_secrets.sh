#!/bin/bash
# Setup Databricks Secrets for Dataverse MCP Server
# This script reads credentials from .env.local and stores them in Databricks Secrets

set -e

echo "========================================="
echo "Databricks Secrets Setup for Dataverse"
echo "========================================="
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
  echo "❌ Error: .env.local file not found!"
  echo "Please create .env.local with your Dataverse credentials first."
  exit 1
fi

# Load variables from .env.local
echo "📖 Reading credentials from .env.local..."
source .env.local

# Map variable names (handle both naming conventions)
DATAVERSE_HOST="${DATAVERSE_HOST:-$DYNAMICS_URL}"
DATAVERSE_TENANT_ID="${DATAVERSE_TENANT_ID:-$TENANT_ID}"
DATAVERSE_CLIENT_ID="${DATAVERSE_CLIENT_ID:-$CLIENT_ID}"
DATAVERSE_CLIENT_SECRET="${DATAVERSE_CLIENT_SECRET:-$CLIENT_SECRET}"

# Validate required variables
if [ -z "$DATAVERSE_HOST" ] || [ -z "$DATAVERSE_TENANT_ID" ] || [ -z "$DATAVERSE_CLIENT_ID" ] || [ -z "$DATAVERSE_CLIENT_SECRET" ]; then
  echo "❌ Error: Missing required credentials in .env.local"
  echo ""
  echo "Required variables (use either naming convention):"
  echo "  - DATAVERSE_HOST or DYNAMICS_URL"
  echo "  - DATAVERSE_TENANT_ID or TENANT_ID"
  echo "  - DATAVERSE_CLIENT_ID or CLIENT_ID"
  echo "  - DATAVERSE_CLIENT_SECRET or CLIENT_SECRET"
  exit 1
fi

echo "✅ Found credentials:"
echo "   Host: $DATAVERSE_HOST"
echo "   Tenant ID: ${DATAVERSE_TENANT_ID:0:8}..."
echo "   Client ID: ${DATAVERSE_CLIENT_ID:0:8}..."
echo "   Client Secret: ****** (hidden)"
echo ""

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
  echo "❌ Error: Databricks CLI not found!"
  echo "Install it with: pip install databricks-cli"
  exit 1
fi

# Check if databricks CLI is configured
if ! databricks current-user me &> /dev/null; then
  echo "❌ Error: Databricks CLI not configured!"
  echo "Run: databricks configure --token"
  exit 1
fi

echo "✅ Databricks CLI is configured"
echo ""

# Prompt for secret scope name
read -p "Enter Databricks secret scope name [dataverse]: " SCOPE_NAME
SCOPE_NAME=${SCOPE_NAME:-dataverse}

echo ""
echo "========================================="
echo "Creating Secret Scope: $SCOPE_NAME"
echo "========================================="
echo ""

# Create secret scope (ignore error if already exists)
if databricks secrets create-scope "$SCOPE_NAME" 2>/dev/null; then
  echo "✅ Created secret scope: $SCOPE_NAME"
else
  echo "ℹ️  Secret scope '$SCOPE_NAME' already exists (this is fine)"
fi

echo ""
echo "========================================="
echo "Storing Secrets"
echo "========================================="
echo ""

# Function to store secret
store_secret() {
  local key=$1
  local value=$2

  echo "📝 Storing secret: $key"
  printf "%s" "$value" | databricks secrets put-secret "$SCOPE_NAME" "$key" 2>/dev/null || \
    printf "%s" "$value" | databricks secrets put "$SCOPE_NAME" "$key"
  echo "✅ Stored: $key"
}

# Store each credential
store_secret "host" "$DATAVERSE_HOST"
store_secret "tenant_id" "$DATAVERSE_TENANT_ID"
store_secret "client_id" "$DATAVERSE_CLIENT_ID"
store_secret "client_secret" "$DATAVERSE_CLIENT_SECRET"

# Store optional variables if they exist
if [ -n "$OAUTH_SCOPE" ]; then
  store_secret "oauth_scope" "$OAUTH_SCOPE"
fi

if [ -n "$TOKEN_ENDPOINT" ]; then
  store_secret "token_endpoint" "$TOKEN_ENDPOINT"
fi

echo ""
echo "========================================="
echo "Verifying Secrets"
echo "========================================="
echo ""

# List secrets to verify
echo "📋 Secrets in scope '$SCOPE_NAME':"
databricks secrets list-secrets --scope "$SCOPE_NAME" | tail -n +2 || \
  databricks secrets list "$SCOPE_NAME"

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit app.yaml and uncomment the secret references:"
echo "   - Uncomment the 'value_from' sections for Dataverse variables"
echo "   - Make sure scope name matches: $SCOPE_NAME"
echo ""
echo "2. Deploy to Databricks:"
echo "   ./deploy.sh --create"
echo ""
echo "3. Check app status:"
echo "   ./app_status.sh"
echo ""
echo "Note: The secrets are now stored securely in Databricks."
echo "Your .env.local file is only for local development."
echo ""

