#!/bin/bash
# Setup script for Dataverse MCP Server deployment to Databricks

set -e

echo "========================================="
echo "🚀 Dataverse MCP Server Setup"
echo "========================================="
echo ""
echo "This script will configure:"
echo "  1. Databricks CLI authentication"
echo "  2. Deployment settings (app name, code path)"
echo "  3. Dataverse credentials (optional)"
echo ""

# Function to prompt with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    read -p "$prompt [$default]: " input
    if [ -z "$input" ]; then
        input="$default"
    fi
    eval "$var_name='$input'"
}

# Function to update .env.local
update_env_value() {
    local key="$1"
    local value="$2"
    
    if [ ! -f .env.local ]; then
        touch .env.local
    fi
    
    if grep -q "^${key}=" .env.local 2>/dev/null; then
        # Update existing value
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^${key}=.*|${key}=${value}|" .env.local
        else
            sed -i "s|^${key}=.*|${key}=${value}|" .env.local
        fi
    else
        echo "${key}=${value}" >> .env.local
    fi
}

# ========================================
# Step 1: Check Prerequisites
# ========================================
echo "========================================="
echo "Step 1: Checking Prerequisites"
echo "========================================="
echo ""

# Check for databricks CLI
if ! command -v databricks &> /dev/null; then
    echo "❌ Databricks CLI not found!"
    echo ""
    echo "Please install it:"
    echo "  pip install databricks-cli"
    echo "  # or"
    echo "  brew install databricks"
    exit 1
fi

DATABRICKS_VERSION=$(databricks --version 2>&1 | head -n1)
echo "✅ Databricks CLI found: $DATABRICKS_VERSION"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅ Python found: $PYTHON_VERSION"
echo ""

# ========================================
# Step 2: Databricks CLI Configuration
# ========================================
echo "========================================="
echo "Step 2: Databricks CLI Configuration"
echo "========================================="
echo ""

# Check if already configured
if databricks current-user me &> /dev/null; then
    echo "ℹ️  Databricks CLI is already configured"
    CURRENT_USER=$(databricks current-user me --output json 2>/dev/null | grep -o '"user_name":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
    CURRENT_HOST=$(databricks auth env --output json 2>/dev/null | grep -o '"host":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
    echo "   Current user: $CURRENT_USER"
    echo "   Current host: $CURRENT_HOST"
    echo ""
    
    read -p "Reconfigure Databricks CLI? (y/N): " RECONFIG
    if [[ ! $RECONFIG =~ ^[Yy]$ ]]; then
        echo "✅ Using existing Databricks CLI configuration"
        DATABRICKS_HOST="$CURRENT_HOST"
        
        # Get token from environment or config
        if [ -n "$DATABRICKS_TOKEN" ]; then
            echo "✅ Using DATABRICKS_TOKEN from environment"
        else
            echo "ℹ️  Using token from Databricks CLI config"
        fi
        echo ""
    else
        DATABRICKS_CLI_CONFIGURED=false
    fi
else
    DATABRICKS_CLI_CONFIGURED=false
fi

# Configure if needed
if [ "$DATABRICKS_CLI_CONFIGURED" = false ]; then
    echo "Let's configure your Databricks connection:"
    echo ""
    
    # Get host
    prompt_with_default "Databricks workspace URL" "https://your-workspace.cloud.databricks.com" DATABRICKS_HOST
    
    # Choose auth method
    echo ""
    echo "Authentication method:"
    echo "  1) Personal Access Token (PAT) - Recommended"
    echo "  2) OAuth (experimental)"
    prompt_with_default "Choose authentication method" "1" AUTH_METHOD
    
    if [ "$AUTH_METHOD" = "1" ]; then
        echo ""
        echo "Creating a Personal Access Token (PAT):"
        echo "  1. Go to: $DATABRICKS_HOST/setting/account/token-management"
        echo "  2. Click 'Generate new token'"
        echo "  3. Copy the token value"
        echo ""
        read -sp "Enter your Databricks PAT: " DATABRICKS_TOKEN
        echo ""
        
        # Configure CLI
        export DATABRICKS_HOST
        export DATABRICKS_TOKEN
        
        # Test connection
        echo ""
        echo "🔍 Testing connection..."
        if databricks current-user me >/dev/null 2>&1; then
            echo "✅ Successfully connected to Databricks!"
            CURRENT_USER=$(databricks current-user me --output json 2>/dev/null | grep -o '"user_name":"[^"]*"' | cut -d'"' -f4)
            echo "   Authenticated as: $CURRENT_USER"
        else
            echo "❌ Failed to connect. Please check your credentials."
            exit 1
        fi
    else
        echo ""
        echo "Configuring OAuth..."
        databricks configure --token --host "$DATABRICKS_HOST"
    fi
    
    echo ""
    echo "✅ Databricks CLI configured"
fi

# Save to .env.local for local development
update_env_value "DATABRICKS_HOST" "$DATABRICKS_HOST"
if [ -n "$DATABRICKS_TOKEN" ]; then
    update_env_value "DATABRICKS_TOKEN" "$DATABRICKS_TOKEN"
fi

echo ""

# ========================================
# Step 3: Deployment Settings
# ========================================
echo "========================================="
echo "Step 3: Deployment Settings"
echo "========================================="
echo ""

# Get current user for default code path
CURRENT_USER_EMAIL=$(databricks current-user me --output json 2>/dev/null | grep -o '"user_name":"[^"]*"' | cut -d'"' -f4 || echo "user@example.com")
DEFAULT_CODE_PATH="/Workspace/Users/${CURRENT_USER_EMAIL}/dataverse_mcp_server"

prompt_with_default "App name (must start with 'mcp-')" "mcp-dataverse-dev" APP_NAME
prompt_with_default "Code path in Databricks workspace" "$DEFAULT_CODE_PATH" CODE_PATH

# Validate app name
if [[ ! $APP_NAME =~ ^mcp- ]]; then
    echo "⚠️  Warning: App name should start with 'mcp-'"
    read -p "Continue anyway? (y/N): " CONTINUE
    if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Save deployment settings (use correct variable names for deploy.sh)
update_env_value "DATABRICKS_APP_NAME" "$APP_NAME"
update_env_value "DBA_SOURCE_CODE_PATH" "$CODE_PATH"

echo ""
echo "✅ Deployment settings configured"
echo ""

# ========================================
# Step 4: Dataverse Credentials (Optional)
# ========================================
echo "========================================="
echo "Step 4: Dataverse Credentials"
echo "========================================="
echo ""

# Check if .env.local already has Dataverse credentials
HAS_DATAVERSE_CREDS=false
if [ -f .env.local ]; then
    if grep -q "DATAVERSE_HOST\|DYNAMICS_URL" .env.local 2>/dev/null; then
        echo "ℹ️  Dataverse credentials found in .env.local"
        HAS_DATAVERSE_CREDS=true
    fi
fi

if [ "$HAS_DATAVERSE_CREDS" = true ]; then
    read -p "Update Dataverse credentials? (y/N): " UPDATE_DATAVERSE
    if [[ ! $UPDATE_DATAVERSE =~ ^[Yy]$ ]]; then
        echo "✅ Using existing Dataverse credentials"
        CONFIGURE_DATAVERSE=false
    else
        CONFIGURE_DATAVERSE=true
    fi
else
    echo "Would you like to configure Dataverse credentials now?"
    echo "(You can also run ./setup_dataverse.sh later)"
    echo ""
    read -p "Configure Dataverse credentials? (Y/n): " CONFIGURE_DATAVERSE_INPUT
    if [[ $CONFIGURE_DATAVERSE_INPUT =~ ^[Nn]$ ]]; then
        CONFIGURE_DATAVERSE=false
    else
        CONFIGURE_DATAVERSE=true
    fi
fi

if [ "$CONFIGURE_DATAVERSE" = true ]; then
    echo ""
    prompt_with_default "Dataverse Host" "https://org1bfe9c69.api.crm.dynamics.com" DATAVERSE_HOST_INPUT
    prompt_with_default "Azure AD Tenant ID" "" TENANT_ID
    prompt_with_default "App Registration Client ID" "" CLIENT_ID
    read -sp "App Registration Client Secret: " CLIENT_SECRET
    echo ""
    
    # Save to .env.local
    update_env_value "DATAVERSE_HOST" "$DATAVERSE_HOST_INPUT"
    update_env_value "DATAVERSE_TENANT_ID" "$TENANT_ID"
    update_env_value "DATAVERSE_CLIENT_ID" "$CLIENT_ID"
    update_env_value "DATAVERSE_CLIENT_SECRET" "$CLIENT_SECRET"
    
    echo ""
    echo "✅ Dataverse credentials saved to .env.local"
else
    echo "⏭️  Skipping Dataverse configuration"
    echo "   Run ./setup_dataverse.sh when ready"
fi

echo ""

# ========================================
# Step 5: Summary and Next Steps
# ========================================
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Configuration Summary:"
echo "  • Databricks Host: $DATABRICKS_HOST"
echo "  • App Name: $APP_NAME"
echo "  • Code Path: $CODE_PATH"
if [ "$CONFIGURE_DATAVERSE" = true ]; then
    echo "  • Dataverse: Configured ✅"
else
    echo "  • Dataverse: Not configured (run ./setup_dataverse.sh)"
fi
echo ""
echo "Configuration saved to: .env.local"
echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""

if [ "$CONFIGURE_DATAVERSE" = true ]; then
    echo "1. Test Dataverse connection:"
    echo "   python test_dataverse.py"
    echo ""
    echo "2. Push credentials to Databricks Secrets:"
    echo "   ./setup_databricks_secrets.sh"
    echo ""
    echo "3. Deploy to Databricks:"
    echo "   ./deploy.sh --create"
else
    echo "1. Configure Dataverse credentials:"
    echo "   ./setup_dataverse.sh"
    echo ""
    echo "2. Test connection:"
    echo "   python test_dataverse.py"
    echo ""
    echo "3. Push credentials to Databricks Secrets:"
    echo "   ./setup_databricks_secrets.sh"
    echo ""
    echo "4. Deploy to Databricks:"
    echo "   ./deploy.sh --create"
fi

echo ""
echo "4. Check deployment status:"
echo "   ./app_status.sh"
echo ""
echo "For local development:"
echo "   ./watch.sh"
echo ""

# Cleanup backup file
rm -f setup.sh.backup

exit 0

