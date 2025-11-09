#!/bin/bash
# Setup script for Dataverse MCP Server

set -e

echo "========================================="
echo "Dataverse MCP Server Setup"
echo "========================================="
echo ""

# Check if .env.local already exists
if [ -f ".env.local" ]; then
  echo "⚠️  .env.local already exists!"
  read -p "Do you want to overwrite it? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled. Your existing .env.local was not modified."
    exit 0
  fi
fi

# Prompt for Dataverse configuration
echo "Please enter your Dataverse configuration:"
echo ""

read -p "Dataverse Host (e.g., https://org1bfe9c69.api.crm.dynamics.com): " DATAVERSE_HOST
read -p "Azure AD Tenant ID: " DATAVERSE_TENANT_ID
read -p "App Registration Client ID: " DATAVERSE_CLIENT_ID
read -sp "App Registration Client Secret: " DATAVERSE_CLIENT_SECRET
echo ""

# Validate inputs
if [ -z "$DATAVERSE_HOST" ] || [ -z "$DATAVERSE_TENANT_ID" ] || [ -z "$DATAVERSE_CLIENT_ID" ] || [ -z "$DATAVERSE_CLIENT_SECRET" ]; then
  echo "❌ Error: All fields are required!"
  exit 1
fi

# Create .env.local file
cat > .env.local << EOF
# Dataverse MCP Server Configuration
# Generated on $(date)

# Dataverse Environment URL
DATAVERSE_HOST=$DATAVERSE_HOST

# Azure AD Credentials
DATAVERSE_TENANT_ID=$DATAVERSE_TENANT_ID
DATAVERSE_CLIENT_ID=$DATAVERSE_CLIENT_ID
DATAVERSE_CLIENT_SECRET=$DATAVERSE_CLIENT_SECRET

# Optional: MCP Server Name
SERVERNAME=dataverse-mcp-server
EOF

echo ""
echo "✅ Configuration saved to .env.local"
echo ""

# Test the connection
echo "========================================="
echo "Testing Dataverse Connection..."
echo "========================================="
echo ""

if command -v python3 &> /dev/null; then
  python3 test_dataverse.py
elif command -v python &> /dev/null; then
  python test_dataverse.py
else
  echo "⚠️  Python not found. Please install Python 3 to run connection tests."
  echo "You can manually test the connection by running: python test_dataverse.py"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review DATAVERSE_SETUP.md for detailed configuration"
echo "2. Start the MCP server: ./watch.sh"
echo "3. Access API docs: http://localhost:8000/docs"
echo "4. MCP endpoint: http://localhost:8000/mcp"
echo ""

