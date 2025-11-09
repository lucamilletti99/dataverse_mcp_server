# Dataverse MCP Server Prompts

This directory contains prompt templates used by the Dataverse MCP Server agent.

## Files

### `dataverse_agent_system.md`
The system prompt used by the Databricks Foundation Model agent when interacting with Dataverse.

**Purpose:**
- Provides context about available Dataverse tools
- Lists common Dataverse table names
- Shows FetchXML query examples
- Defines best practices for querying data

**Usage:**
This prompt is automatically loaded by `server/routers/agent_chat.py` at runtime. To modify the agent's behavior, edit this markdown file and redeploy.

**Editing:**
1. Update `dataverse_agent_system.md` with your changes
2. Run `./deploy.sh` to deploy
3. Test the agent's new behavior

**Benefits:**
- ✅ **Version control** - Track prompt changes in git
- ✅ **Easy iteration** - Edit markdown without touching Python code
- ✅ **Separation of concerns** - Prompts separate from business logic
- ✅ **Team collaboration** - Non-technical users can suggest prompt improvements

## Best Practices

### System Prompt Guidelines:
1. **Be specific** - Include concrete examples (FetchXML queries, table names)
2. **Show workflows** - Describe step-by-step processes (describe → query → format)
3. **Provide context** - List common entities, operators, syntax rules
4. **Set expectations** - Clearly state what tools do and when to use them

### What to Include:
- Tool descriptions and capabilities
- Common entity/table names in the Dataverse environment
- Query syntax examples (FetchXML)
- Workflow patterns (e.g., "always describe before querying")
- Best practices and constraints

### What to Avoid:
- Overly generic instructions
- Ambiguous tool descriptions
- Missing examples
- Contradictory guidance

## Future Extensions

You can add more prompt files here:
- `dataverse_agent_user.md` - User-facing prompt template
- `dataverse_agent_functions.md` - Function-specific guidance
- `dataverse_agent_errors.md` - Error handling guidance

Update `server/routers/agent_chat.py` to load additional prompt files as needed.

