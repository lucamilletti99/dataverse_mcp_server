# Dataverse MCP Server Setup Guide

This guide will help you configure and test the Dataverse MCP server.

## Prerequisites

### 1. Dataverse Environment

You need access to a Microsoft Dataverse environment:
- **Environment URL:** Your organization's Dataverse URL (e.g., `https://org1bfe9c69.api.crm.dynamics.com`)
- **Access Level:** You'll need appropriate permissions to read/write data

### 2. Azure AD App Registration

You need a Service Principal (app registration) with permissions to access Dataverse:

#### Create App Registration:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Name: `Dataverse MCP Server` (or your preferred name)
5. Supported account types: **Single tenant**
6. Click **Register**

#### Get Credentials:

After registration, collect these values:

- **Application (client) ID** → This is your `DATAVERSE_CLIENT_ID`
- **Directory (tenant) ID** → This is your `DATAVERSE_TENANT_ID`

#### Create Client Secret:

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "MCP Server Secret")
4. Choose expiration period (e.g., 24 months)
5. Click **Add**
6. **Copy the secret value immediately** → This is your `DATAVERSE_CLIENT_SECRET`
   - ⚠️ You cannot view it again after leaving this page!

#### Configure API Permissions:

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Dynamics CRM** (or **Common Data Service**)
4. Select **Delegated permissions** (or **Application permissions** for service-to-service)
5. Check **user_impersonation** permission
6. Click **Add permissions**
7. Click **Grant admin consent** (requires admin privileges)

#### Configure Dataverse Application User:

Your Service Principal needs to be registered as an application user in Dataverse:

1. Go to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/)
2. Select your environment
3. Go to **Settings** → **Users + permissions** → **Application users**
4. Click **New app user**
5. Click **Add an app**
6. Search for your app registration by name or client ID
7. Select it and click **Add**
8. Assign a security role (e.g., **System Administrator** or custom role with appropriate permissions)
9. Click **Create**

Reference: [Create an application user](https://learn.microsoft.com/en-us/power-platform/admin/manage-application-users#create-an-application-user)

---

## Configuration

### 1. Create `.env.local` File

Copy the example environment file:

```bash
cp .env.example .env.local
```

### 2. Fill in Your Credentials

Edit `.env.local` with your actual values:

```bash
# Dataverse Environment URL
DATAVERSE_HOST=https://org1bfe9c69.api.crm.dynamics.com

# Azure AD Credentials
DATAVERSE_TENANT_ID=your-tenant-id-guid
DATAVERSE_CLIENT_ID=your-client-id-guid
DATAVERSE_CLIENT_SECRET=your-client-secret-value
```

**Important:** The `DATAVERSE_HOST` should be your Dataverse organization URL without any path segments.

---

## Testing the Connection

### 1. Install Dependencies

Make sure you have all required Python packages:

```bash
uv pip install requests python-dotenv
```

### 2. Run Test Script

Test your Dataverse connection:

```bash
python test_dataverse.py
```

The test script will:
1. ✅ Authenticate with Azure AD
2. ✅ List Dataverse tables
3. ✅ Describe the `account` table
4. ✅ Query account records (if any exist)

**Expected Output:**

```
================================================================================
DATAVERSE MCP SERVER - CONNECTION TESTS
================================================================================

✅ All required environment variables are set

================================================================================
TEST 1: Authentication
================================================================================
🔐 Acquiring new Dataverse access token...
   Tenant ID: your-tenant-id
   Client ID: your-client-id
   Scope: https://org1bfe9c69.api.crm.dynamics.com/.default
✅ Successfully obtained access token (expires in 3599s)
✅ Access token obtained

================================================================================
TEST 2: List Tables
================================================================================
📡 Dataverse API Request: GET EntityDefinitions
✅ Retrieved 5 tables
   - account (Account) → accounts
   - contact (Contact) → contacts
   ...

================================================================================
TEST SUMMARY
================================================================================
✅ PASS - Authentication
✅ PASS - List Tables
✅ PASS - Describe Table
✅ PASS - Read Query

Total: 4/4 tests passed

🎉 All tests passed! Dataverse MCP server is ready.
```

---

## Running the MCP Server

### Local Development

Start the server locally:

```bash
./watch.sh
```

or manually:

```bash
uvicorn server.app:combined_app --reload --host 0.0.0.0 --port 8000
```

The MCP server will be available at:
- **MCP Endpoint:** `http://localhost:8000/mcp`
- **API Docs:** `http://localhost:8000/docs`

### Test MCP Tools

You can test the MCP tools via the FastAPI docs interface:

1. Open `http://localhost:8000/docs`
2. Expand the MCP sections
3. Try the tools:
   - `GET /mcp/list-tools` - See all available tools
   - `POST /mcp/call-tool` - Call a tool with parameters

Example tool call:

```json
{
  "name": "list_tables",
  "arguments": {
    "top": 10
  }
}
```

---

## Available MCP Tools (Phase 1)

### Core Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `health` | Check server status | `health()` |
| `list_tables` | List all Dataverse tables | `list_tables(top=20)` |
| `describe_table` | Get table schema | `describe_table("account")` |
| `read_query` | Query records | `read_query("account", select=["name"], top=10)` |
| `create_record` | Create new record | `create_record("account", {"name": "Contoso"})` |
| `update_record` | Update existing record | `update_record("account", "guid", {"revenue": 1000000})` |

### Stub Tools (Phase 2 - Not Yet Implemented)

- `list_knowledge_sources`
- `retrieve_knowledge`
- `list_prompts`
- `execute_prompt`

---

## Troubleshooting

### Authentication Errors

**Error:** `Failed to obtain Dataverse access token: 401 Unauthorized`

**Solutions:**
1. Verify your `DATAVERSE_CLIENT_ID` and `DATAVERSE_CLIENT_SECRET` are correct
2. Check that the client secret hasn't expired
3. Ensure you've granted admin consent for API permissions
4. Verify the app registration has the correct API permissions

---

**Error:** `Invalid client secret provided`

**Solutions:**
1. Create a new client secret in Azure Portal
2. Update `DATAVERSE_CLIENT_SECRET` in `.env.local`
3. Secrets cannot be retrieved after creation - you must create a new one

---

### Permission Errors

**Error:** `Principal user is missing prvRead privilege`

**Solutions:**
1. Go to Power Platform Admin Center
2. Settings → Users + permissions → Application users
3. Find your app user
4. Click **Manage roles**
5. Assign appropriate security role (e.g., System Administrator)

---

**Error:** `403 Forbidden` when querying tables

**Solutions:**
1. Your application user needs appropriate permissions in Dataverse
2. Ensure the security role assigned includes:
   - Read privilege for the tables you want to query
   - Write privilege if you want to create/update records

---

### Connection Errors

**Error:** `Connection timeout` or `Could not reach endpoint`

**Solutions:**
1. Check your `DATAVERSE_HOST` is correct
2. Ensure you're using the API endpoint (e.g., `https://orgXXXX.api.crm.dynamics.com`)
3. Verify your network allows outbound HTTPS connections
4. Check if your organization uses a firewall or proxy

---

**Error:** `Table 'account' not found`

**Solutions:**
1. The table might not exist in your environment
2. Use `list_tables()` to see available tables
3. Standard tables: `account`, `contact`, `lead`, `opportunity`
4. Custom tables have naming pattern: `cr123_customname`

---

## Next Steps

Once your connection tests pass:

1. **Test MCP Tools:** Use the `/docs` interface to test individual tools
2. **Connect from Claude Desktop:** Configure Claude to use your MCP server (see main README)
3. **Build Custom Queries:** Use `read_query` with OData filters for complex data retrieval
4. **Integrate with Applications:** Use the MCP HTTP endpoint from your applications

---

## Reference Links

- [Dataverse Web API Documentation](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview)
- [Authenticate with Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth)
- [Application Users in Dataverse](https://learn.microsoft.com/en-us/power-platform/admin/manage-application-users)
- [Dataverse Security Roles](https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

