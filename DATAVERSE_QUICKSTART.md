# Dataverse MCP Server - Quick Start Guide

This is a **5-minute quick start** to get your Dataverse MCP server running locally.

## What You Need

Before starting, gather these credentials:

| Credential | Where to Find |
|------------|---------------|
| **Dataverse Host** | Your org URL: `https://orgXXXX.api.crm.dynamics.com` |
| **Tenant ID** | Azure Portal → Azure AD → Overview |
| **Client ID** | Azure Portal → App Registrations → Your App |
| **Client Secret** | Azure Portal → App Registrations → Certificates & secrets |

> **Don't have these?** See [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md) for detailed Azure AD setup instructions.

---

## Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install fastapi uvicorn requests python-dotenv fastmcp

# Or with uv (recommended)
uv pip install fastapi uvicorn requests python-dotenv fastmcp
```

---

## Step 2: Configure Credentials

### Option A: Automated Setup (Recommended)

Run the setup script:

```bash
chmod +x setup_dataverse.sh
./setup_dataverse.sh
```

The script will:
1. Prompt for your credentials
2. Create `.env.local` with your configuration
3. Test the connection automatically

### Option B: Manual Setup

Create `.env.local` file:

```bash
cp env.example .env.local
```

Edit `.env.local`:

```bash
DATAVERSE_HOST=https://org1bfe9c69.api.crm.dynamics.com
DATAVERSE_TENANT_ID=your-tenant-id-guid
DATAVERSE_CLIENT_ID=your-client-id-guid
DATAVERSE_CLIENT_SECRET=your-client-secret-value
```

---

## Step 3: Test Connection

Run the test script:

```bash
python test_dataverse.py
```

**Expected output:**

```
✅ All required environment variables are set
✅ Authentication
✅ List Tables
✅ Describe Table
✅ Read Query

🎉 All tests passed! Dataverse MCP server is ready.
```

**If tests fail:** See [Troubleshooting](#troubleshooting) below.

---

## Step 4: Start MCP Server

### Local Development

```bash
# Option 1: With hot reload (development)
./watch.sh

# Option 2: Direct uvicorn
uvicorn server.app:combined_app --reload --port 8000
```

Server endpoints:
- 🌐 **API Docs:** http://localhost:8000/docs
- 🔧 **MCP Endpoint:** http://localhost:8000/mcp
- ❤️ **Health Check:** http://localhost:8000/api/health

---

## Step 5: Test MCP Tools

### Via API Docs (Browser)

1. Open http://localhost:8000/docs
2. Try the `list_tables` tool:
   - Expand `POST /mcp/call-tool`
   - Click **Try it out**
   - Request body:
     ```json
     {
       "name": "list_tables",
       "arguments": {
         "top": 10
       }
     }
     ```
   - Click **Execute**

### Via cURL (Terminal)

```bash
# Health check
curl http://localhost:8000/api/health

# List MCP tools
curl http://localhost:8000/mcp/list-tools

# Call list_tables tool
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_tables",
    "arguments": {"top": 10}
  }'
```

---

## Available MCP Tools

| Tool | Description | Example |
|------|-------------|---------|
| `health` | Server health check | `health()` |
| `list_tables` | List all tables | `list_tables(top=20)` |
| `describe_table` | Get table schema | `describe_table("account")` |
| `read_query` | Query records | `read_query("account", select=["name"], top=10)` |
| `create_record` | Create record | `create_record("account", {"name": "Contoso"})` |
| `update_record` | Update record | `update_record("account", "guid", {"revenue": 1000000})` |

---

## Connect from Claude Desktop

### 1. Configure Claude Desktop

Edit your Claude configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "dataverse": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 2. Restart Claude Desktop

Close and reopen Claude Desktop app.

### 3. Test in Claude

Try these prompts:

```
"List all tables in Dataverse"
"Show me the schema for the account table"
"Query the top 5 accounts"
```

---

## Example Queries

### List Custom Tables Only

```python
list_tables(custom_only=True, top=50)
```

### Get Account Schema

```python
describe_table("account")
```

### Query Accounts with Filter

```python
read_query(
    table_name="account",
    select=["name", "revenue", "industry"],
    filter_query="revenue gt 1000000",
    order_by="name asc",
    top=20
)
```

### Create a New Account

```python
create_record(
    table_name="account",
    data={
        "name": "Contoso Ltd",
        "revenue": 5000000,
        "industry": "Technology"
    }
)
```

### Update an Account

```python
update_record(
    table_name="account",
    record_id="12345678-1234-1234-1234-123456789abc",
    data={
        "revenue": 6000000,
        "industry": "Software"
    }
)
```

---

## Troubleshooting

### Authentication Fails

**Symptom:** `Failed to obtain Dataverse access token: 401`

**Fix:**
1. Verify `DATAVERSE_CLIENT_ID` and `DATAVERSE_CLIENT_SECRET` are correct
2. Check client secret hasn't expired (create new one in Azure Portal)
3. Ensure API permissions are granted with admin consent

### Permission Denied

**Symptom:** `Principal user is missing prvRead privilege`

**Fix:**
1. Go to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/)
2. Select your environment → Settings → Users + permissions → Application users
3. Find your app user and assign security role (e.g., System Administrator)

### Table Not Found

**Symptom:** `Table 'xyz' not found`

**Fix:**
1. Run `list_tables()` to see available tables
2. Use the exact `logical_name` (e.g., `account`, not `accounts`)
3. Custom tables have prefix like `cr123_customtable`

### Connection Timeout

**Symptom:** `Connection timeout` or `Could not reach endpoint`

**Fix:**
1. Check `DATAVERSE_HOST` is correct (no trailing slash)
2. Verify network connectivity
3. Check firewall/proxy settings

---

## Next Steps

Once your server is running:

1. ✅ **Read Full Setup Guide:** [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md)
2. 🔐 **Configure Security:** Review Azure AD app permissions
3. 🚀 **Deploy to Databricks:** Use existing `deploy.sh` (if targeting Databricks Apps)
4. 📖 **API Reference:** Check [Dataverse Web API docs](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview)

---

## Getting Help

- **Authentication Issues:** See [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md) → Troubleshooting section
- **API Errors:** Check [Dataverse API docs](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview)
- **MCP Protocol:** See [Model Context Protocol](https://modelcontextprotocol.io/)

---

## What's Next?

You now have a working Dataverse MCP server! The server exposes Dataverse tables and records through the Model Context Protocol, allowing AI assistants like Claude to:

- Discover and query your Dataverse data
- Create and update records
- Understand table schemas
- Execute complex OData queries

**Phase 2 Features (Coming Soon):**
- Knowledge sources integration
- Custom prompts execution
- Batch operations
- Advanced filtering

Enjoy building with Dataverse MCP! 🎉

