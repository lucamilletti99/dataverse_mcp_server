# 🔌 Dataverse MCP Server

A Model Context Protocol (MCP) server for Microsoft Dataverse, enabling AI assistants like Claude to interact with Dataverse data through natural language.

> **Built on:** [Model Context Protocol](https://modelcontextprotocol.io/) | [Microsoft Dataverse MCP Spec](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp)

---

## What is This?

This MCP server exposes Microsoft Dataverse tables and records through the Model Context Protocol, allowing AI assistants to:

- 📊 **List and explore** Dataverse tables (entities)
- 🔍 **Query records** with OData filters and sorting
- ✏️ **Create new records** in any table
- 🔄 **Update existing records** by GUID
- 🤖 **Natural language interface** via Claude Desktop, VS Code, or any MCP client

---

## Quick Start

### 1. Prerequisites

- **Python 3.11+**
- **Dataverse environment** with API access
- **Azure AD app registration** with Dataverse permissions

### 2. Install

```bash
# Install dependencies
pip install fastapi uvicorn requests python-dotenv fastmcp

# Or with uv (recommended)
uv pip install fastapi uvicorn requests python-dotenv fastmcp
```

### 3. Configure

Run the setup script:

```bash
chmod +x setup_dataverse.sh
./setup_dataverse.sh
```

Or manually create `.env.local`:

```bash
DATAVERSE_HOST=https://org1bfe9c69.api.crm.dynamics.com
DATAVERSE_TENANT_ID=your-tenant-id
DATAVERSE_CLIENT_ID=your-client-id
DATAVERSE_CLIENT_SECRET=your-client-secret
```

### 4. Test Connection

```bash
python test_dataverse.py
```

Expected output: `✅ All tests passed! Dataverse MCP server is ready.`

### 5. Start Server

**Option A: Run Locally**

```bash
./watch.sh
# Or: uvicorn server.app:combined_app --reload --port 8000
```

**Option B: Deploy to Databricks Apps**

```bash
./deploy.sh --create
```

📖 See [DATABRICKS_DEPLOYMENT.md](DATABRICKS_DEPLOYMENT.md) for deployment guide.

**Server endpoints:**
- 🔧 MCP: `http://localhost:8000/mcp` (local) or `https://your-app.databricksapps.com/apps/your-app/mcp` (cloud)
- 📖 Docs: `http://localhost:8000/docs`
- ❤️ Health: `http://localhost:8000/api/health`

---

## Documentation

| Document | Description |
|----------|-------------|
| **[DATAVERSE_QUICKSTART.md](DATAVERSE_QUICKSTART.md)** | 5-minute quick start guide |
| **[DATAVERSE_SETUP.md](DATAVERSE_SETUP.md)** | Detailed Azure AD & Dataverse setup |
| **[DATABRICKS_DEPLOYMENT.md](DATABRICKS_DEPLOYMENT.md)** | Deploy to Databricks Apps |
| **[README_DATAVERSE.md](README_DATAVERSE.md)** | Complete reference documentation |

---

## Available MCP Tools

### Phase 1 (Implemented)

| Tool | Description |
|------|-------------|
| `health` | Server health check |
| `list_tables` | List all Dataverse tables |
| `describe_table` | Get table schema and columns |
| `read_query` | Query records with OData filters |
| `create_record` | Create new records |
| `update_record` | Update existing records |

### Phase 2 (Planned)

- `delete_record` - Delete records
- `create_table` / `update_table` / `delete_table` - Table management
- `list_knowledge_sources` / `retrieve_knowledge` - Copilot Studio integration
- `list_prompts` / `execute_prompt` - Custom prompts

---

## Usage Examples

### Claude Desktop

Configure `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dataverse": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Then in Claude:

```
You: "List all custom tables in my Dataverse environment"
Claude: [Calls list_tables with custom_only=True]

You: "Show me accounts with revenue over $1M"
Claude: [Calls read_query with filter]

You: "Create a new account called Fabrikam with $2M revenue"
Claude: [Calls create_record]
```

### cURL

```bash
# List tables
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{"name": "list_tables", "arguments": {"top": 10}}'

# Query accounts
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "read_query",
    "arguments": {
      "table_name": "account",
      "select": ["name", "revenue"],
      "filter_query": "revenue gt 1000000",
      "top": 10
    }
  }'
```

### Python

```python
import requests

response = requests.post('http://localhost:8000/mcp/call-tool', json={
    "name": "describe_table",
    "arguments": {"table_name": "account"}
})

print(response.json())
```

---

## Project Structure

```
dataverse_mcp_server/
├── server/
│   ├── app.py                      # FastAPI + MCP server
│   ├── dataverse_tools.py          # MCP tool implementations
│   ├── dataverse/
│   │   ├── auth.py                 # OAuth authentication
│   │   ├── client.py               # Dataverse Web API client
│   │   └── __init__.py
│   └── routers/                    # FastAPI REST endpoints
│       ├── health.py               # Health check
│       ├── mcp_info.py             # MCP metadata
│       └── user.py                 # User info
├── client/                         # React frontend (future)
├── test_dataverse.py              # Connection tests
├── setup_dataverse.sh             # Interactive setup
├── watch.sh                       # Dev server with hot reload
├── config.yaml                    # MCP server config
├── env.example                    # Environment template
├── DATAVERSE_QUICKSTART.md        # Quick start guide
├── DATAVERSE_SETUP.md             # Detailed setup
└── README_DATAVERSE.md            # Full reference
```

---

## Architecture

**Authentication:** Service Principal (OAuth 2.0 client credentials flow)  
**API:** Dataverse Web API v9.2  
**Protocol:** Model Context Protocol (MCP)  
**Framework:** FastAPI + FastMCP

```
MCP Clients (Claude, VS Code) 
    ↓ HTTP/MCP
Dataverse MCP Server (FastAPI)
    ↓ HTTPS/OAuth
Microsoft Dataverse
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **401 Authentication Error** | Check client secret validity and API permissions |
| **403 Permission Denied** | Assign security role to app user in Power Platform Admin Center |
| **Table Not Found** | Use `list_tables()` to find correct logical name |
| **Connection Timeout** | Verify `DATAVERSE_HOST` and network connectivity |

See [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md#troubleshooting) for detailed troubleshooting.

---

## Development

```bash
# Run tests
python test_dataverse.py

# Start dev server
./watch.sh

# Check lints
ruff check server/

# Format code
ruff format server/
```

---

## Reference Links

- [Dataverse Web API Documentation](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Microsoft Dataverse MCP](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp)
- [OAuth with Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth)

---

## License

See [LICENSE.md](LICENSE.md)

## Security

Report vulnerabilities via [SECURITY.md](SECURITY.md)

---

**Questions?** See [DATAVERSE_QUICKSTART.md](DATAVERSE_QUICKSTART.md) or [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md)

**Built with ❤️ for the Dataverse and MCP communities**
