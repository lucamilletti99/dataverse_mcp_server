# Deploying Dataverse MCP Server to Databricks Apps

This guide shows you how to deploy the Dataverse MCP Server as a Databricks App, which allows you to:

- Host the MCP server in the cloud (accessible via HTTPS)
- Share the server with your team
- Scale automatically
- Integrate with Databricks authentication (optional)

---

## Prerequisites

### 1. Databricks Workspace

- **Databricks Apps** enabled (Public Preview)
- **Account** with permission to create apps
- **Databricks CLI** installed and configured

Install Databricks CLI:

```bash
# With pip
pip install databricks-cli

# Or with Homebrew
brew tap databricks/tap
brew install databricks

# Verify
databricks --version  # Should be v0.260.0+
```

Configure CLI:

```bash
databricks configure --token
# Enter your workspace URL and personal access token
```

### 2. Dataverse Credentials

You'll need your Dataverse credentials ready:
- `DATAVERSE_HOST`
- `DATAVERSE_TENANT_ID`
- `DATAVERSE_CLIENT_ID`
- `DATAVERSE_CLIENT_SECRET`

---

## Deployment Options

You have two options for managing Dataverse credentials:

### Option A: Databricks Secrets (Recommended)

Store credentials securely in Databricks Secrets.

#### 1. Create Secret Scope

```bash
databricks secrets create-scope dataverse
```

#### 2. Store Credentials

```bash
databricks secrets put-secret dataverse host
# Paste: https://org1bfe9c69.api.crm.dynamics.com

databricks secrets put-secret dataverse tenant_id
# Paste: your-tenant-id

databricks secrets put-secret dataverse client_id
# Paste: your-client-id

databricks secrets put-secret dataverse client_secret
# Paste: your-client-secret
```

#### 3. Update `app.yaml`

Edit `app.yaml` and uncomment the secrets references:

```yaml
env:
  DATAVERSE_HOST: ${secrets.dataverse.host}
  DATAVERSE_TENANT_ID: ${secrets.dataverse.tenant_id}
  DATAVERSE_CLIENT_ID: ${secrets.dataverse.client_id}
  DATAVERSE_CLIENT_SECRET: ${secrets.dataverse.client_secret}
  SERVERNAME: "dataverse-mcp-server"
```

### Option B: Direct Values (Testing Only)

**⚠️ WARNING:** Only use this for testing. Credentials will be visible to anyone with app access.

Edit `app.yaml`:

```yaml
env:
  DATAVERSE_HOST: "https://org1bfe9c69.api.crm.dynamics.com"
  DATAVERSE_TENANT_ID: "your-tenant-id"
  DATAVERSE_CLIENT_ID: "your-client-id"
  DATAVERSE_CLIENT_SECRET: "your-client-secret"
  SERVERNAME: "dataverse-mcp-server"
```

---

## Deployment Steps

### 1. First Time Deployment

```bash
./deploy.sh --create
```

The script will:
1. ✅ Build the frontend (if applicable)
2. ✅ Package the backend
3. ✅ Create Databricks App
4. ✅ Generate Service Principal
5. ✅ Deploy code
6. ✅ Start the application

**When prompted, enter your app name:**
- Must start with `mcp-` (e.g., `mcp-dataverse-prod`)

### 2. Verify Deployment

Check app status:

```bash
./app_status.sh
```

**Expected output:**

```
App: mcp-dataverse-prod
Status: RUNNING
URL: https://your-workspace.databricksapps.com/apps/mcp-dataverse-prod
Service Principal ID: 00000000-0000-0000-0000-000000000000
```

### 3. Test the App

Open the app URL in your browser. You should see:

- **MCP Endpoint:** `https://your-app-url/mcp`
- **API Docs:** `https://your-app-url/docs`
- **Health Check:** `https://your-app-url/api/health`

---

## Updating the App

After making code changes, redeploy:

```bash
./deploy.sh
# No --create flag needed for updates
```

This updates the existing app without recreating it.

---

## Testing from MCP Clients

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dataverse": {
      "url": "https://your-workspace.databricksapps.com/apps/mcp-dataverse-prod/mcp"
    }
  }
}
```

### VS Code GitHub Copilot

Edit your MCP configuration:

```json
{
  "dataverse": {
    "command": "curl",
    "args": [
      "-X", "POST",
      "https://your-workspace.databricksapps.com/apps/mcp-dataverse-prod/mcp"
    ]
  }
}
```

---

## Monitoring & Debugging

### View Logs

Stream application logs:

```bash
databricks apps logs mcp-dataverse-prod --follow
```

Or view in browser:

```
https://your-app-url/logz
```

### Check Health

```bash
curl https://your-app-url/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "dataverse-mcp-server",
  "dataverse_configured": true,
  "connection_healthy": true,
  "dataverse_host": "https://org1bfe9c69.api.crm.dynamics.com",
  "architecture": "Dataverse Web API v9.2"
}
```

### Restart App

If needed:

```bash
databricks apps restart mcp-dataverse-prod
```

---

## Managing Multiple Environments

Deploy separate instances for dev/staging/prod:

```bash
# Development
./deploy.sh --app-name mcp-dataverse-dev --create

# Staging
./deploy.sh --app-name mcp-dataverse-staging --create

# Production
./deploy.sh --app-name mcp-dataverse-prod --create
```

Use different secret scopes for each:

```bash
databricks secrets create-scope dataverse-dev
databricks secrets create-scope dataverse-staging
databricks secrets create-scope dataverse-prod
```

Update `app.yaml` for each environment accordingly.

---

## Troubleshooting

### Deployment Fails

**Check CLI configuration:**

```bash
databricks current-user me
```

**Check workspace requirements:**
- Databricks Apps must be enabled
- You must have permission to create apps

### App Won't Start

**Check logs:**

```bash
databricks apps logs mcp-dataverse-prod
```

**Common issues:**
- Missing Dataverse credentials
- Invalid secret scope references
- Network connectivity to Dataverse

### "Secret not found" Error

Verify secrets exist:

```bash
databricks secrets list-secrets --scope dataverse
```

Should show:
- host
- tenant_id
- client_id
- client_secret

### Authentication Fails

Test Dataverse connection from Databricks:

```bash
databricks apps execute mcp-dataverse-prod "python test_dataverse.py"
```

---

## Deleting the App

To remove the app:

```bash
databricks apps delete mcp-dataverse-prod
```

This does NOT delete:
- Secret scopes (delete manually if needed)
- Source code in workspace

---

## Security Best Practices

### 1. Use Secrets

Always use Databricks Secrets for production:

```yaml
env:
  DATAVERSE_CLIENT_SECRET: ${secrets.dataverse.client_secret}
```

### 2. Limit Secret Access

Grant secret scope access only to authorized principals:

```bash
databricks secrets put-acl dataverse <principal-id> READ
```

### 3. Rotate Credentials

Regularly rotate Dataverse client secrets:

1. Create new secret in Azure Portal
2. Update Databricks secret: `databricks secrets put-secret dataverse client_secret`
3. Restart app: `databricks apps restart mcp-dataverse-prod`

### 4. Monitor Access

Review app logs regularly:

```bash
databricks apps logs mcp-dataverse-prod --since 24h
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         MCP Clients                     │
│  (Claude, VS Code, Custom Apps)         │
└─────────────────────────────────────────┘
              │ HTTPS/MCP
              ▼
┌─────────────────────────────────────────┐
│      Databricks App (Cloud)             │
│  ┌───────────────────────────────────┐  │
│  │  Dataverse MCP Server (FastAPI)   │  │
│  │  • OAuth with Service Principal   │  │
│  │  • Stateless proxy                │  │
│  │  • Auto-scaling                   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
              │ HTTPS/OAuth
              ▼
┌─────────────────────────────────────────┐
│     Microsoft Dataverse                 │
│     (https://org.api.crm.dynamics.com)  │
└─────────────────────────────────────────┘
```

---

## Cost Considerations

Databricks Apps pricing:
- **Compute:** Charged per DBU (Databricks Unit)
- **Auto-scaling:** App scales based on traffic
- **Idle time:** Minimal cost when not in use

To minimize costs:
- Use smaller instance sizes for low-traffic apps
- Enable auto-pause (if available)
- Share apps across teams instead of per-user deployments

---

## Reference

- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [Databricks Secrets](https://docs.databricks.com/en/security/secrets/index.html)
- [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/index.html)

---

## Next Steps

Once deployed:

1. ✅ Test MCP endpoint from Claude Desktop
2. ✅ Share app URL with team members
3. ✅ Set up monitoring and alerts
4. ✅ Document your Dataverse schema for users

Need help? See [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md) for troubleshooting.

