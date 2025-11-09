"""Agent chat router for Dataverse MCP server."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


def load_system_prompt() -> str:
    """Load the Dataverse agent system prompt from markdown file.
    
    Returns:
        System prompt content as string
    """
    prompt_file = Path(__file__).parent.parent.parent / "prompts" / "dataverse_agent_system.md"
    
    try:
        return prompt_file.read_text()
    except Exception as e:
        # Fallback to inline prompt if file not found
        print(f"⚠️  Could not load system prompt from {prompt_file}: {e}")
        print("   Using inline fallback prompt")
        return (
            "You are a Dataverse AI assistant with access to Microsoft Dataverse data.\n\n"
            "## Available Tools:\n"
            "1. **list_tables** - Discover available tables (entities)\n"
            "2. **describe_table** - Get schema/columns for a specific table\n"
            "3. **read_query** - Query records using FetchXML\n"
            "4. **create_record** - Insert new records\n"
            "5. **update_record** - Modify existing records\n\n"
            "Always use the available tools to access real data - never make up information!"
        )


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class AgentChatRequest(BaseModel):
    """Agent chat request model."""
    messages: List[ChatMessage]
    model: str = "databricks-claude-sonnet-4"
    max_tokens: Optional[int] = 2048
    temperature: Optional[float] = 0.7


class AgentChatResponse(BaseModel):
    """Agent chat response model."""
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    trace_id: Optional[str] = None


def get_databricks_client(request: Request) -> WorkspaceClient:
    """Get Databricks WorkspaceClient, prioritizing OBO token."""
    host = os.environ.get('DATABRICKS_HOST')
    obo_token = request.headers.get('X-Forwarded-Access-Token')

    if obo_token:
        config = Config(host=host, token=obo_token, auth_type='pat')
        return WorkspaceClient(config=config)
    else:
        # Fallback to service principal if no OBO token
        return WorkspaceClient(host=host)


def get_databricks_token(request: Request) -> str:
    """Get Databricks token for API calls."""
    obo_token = request.headers.get('X-Forwarded-Access-Token')
    if obo_token:
        return obo_token
    # Fallback to service principal token
    return os.environ.get('DATABRICKS_TOKEN', '')


def call_foundation_model(
    model_name: str,
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
    temperature: float,
    max_tokens: int,
    token: str,
) -> Dict[str, Any]:
    """Call Databricks Foundation Model API via REST.
    
    Args:
        model_name: Name of the foundation model (e.g., 'databricks-claude-sonnet-4')
        messages: List of chat messages
        tools: List of tool definitions
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        token: Databricks API token
        
    Returns:
        API response as dictionary
    """
    host = os.environ.get('DATABRICKS_HOST', '')
    
    # Ensure host has proper scheme
    if not host.startswith('http://') and not host.startswith('https://'):
        host = f'https://{host}'
    
    # Remove trailing slash if present
    host = host.rstrip('/')
    
    url = f"{host}/serving-endpoints/{model_name}/invocations"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messages": messages,
        "tools": tools,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_detail = f"HTTP {e.response.status_code}"
        try:
            error_body = e.response.json()
            error_detail = f"{error_detail}: {error_body.get('message', error_body)}"
        except:
            error_detail = f"{error_detail}: {e.response.text[:200]}"
        raise Exception(f"Foundation Model API error: {error_detail}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")


@router.post('/chat', response_model=AgentChatResponse)
async def agent_chat(request: Request, chat_request: AgentChatRequest) -> AgentChatResponse:
    """Handle agent chat requests with Databricks Foundation Models.
    
    This endpoint:
    1. Receives chat messages from the frontend
    2. Calls Databricks Foundation Model with tool definitions
    3. Executes any tool calls from the model
    4. Returns the final response
    
    Args:
        request: FastAPI request object (for auth headers)
        chat_request: Chat request with messages and model selection
        
    Returns:
        AgentChatResponse with assistant's response and metadata
    """
    try:
        # Get Databricks token for API calls
        db_token = get_databricks_token(request)
        
        # Validate token
        if not db_token:
            raise HTTPException(
                status_code=401,
                detail="No Databricks authentication token available"
            )
        
        # Import tool implementations
        from server.dataverse_tools import (
            list_tables_impl,
            describe_table_impl,
            read_query_impl,
            create_record_impl,
            update_record_impl,
        )
        
        # Define tools schema for the model
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_tables",
                    "description": "List all tables (entities) in Dataverse. Returns metadata about available tables including logical names, display names, and primary attributes.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filter_query": {
                                "type": "string",
                                "description": "OData filter expression (e.g., 'IsCustomEntity eq true')"
                            },
                            "top": {
                                "type": "integer",
                                "description": "Maximum number of tables to return (default: 100)"
                            },
                            "custom_only": {
                                "type": "boolean",
                                "description": "If True, only return custom tables"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "describe_table",
                    "description": "Get detailed metadata for a specific table (entity). Returns comprehensive information about a table including all its columns (attributes), data types, and relationships.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Logical name of the table (e.g., 'account', 'contact', 'cr123_customtable')"
                            }
                        },
                        "required": ["table_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_query",
                    "description": "Query records from a Dataverse table using FetchXML. Retrieve data from a table using a FetchXML query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Logical name of the table (e.g., 'account', 'contact')"
                            },
                            "fetch_xml": {
                                "type": "string",
                                "description": "The FetchXML query string"
                            }
                        },
                        "required": ["table_name", "fetch_xml"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_record",
                    "description": "Create a new record in a Dataverse table. Insert a new row with the specified field values.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Logical name of the table (e.g., 'account', 'contact')"
                            },
                            "data": {
                                "type": "object",
                                "description": "Record data as dictionary with column names as keys"
                            }
                        },
                        "required": ["table_name", "data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_record",
                    "description": "Update an existing record in a Dataverse table. Modify specific fields of an existing record.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Logical name of the table (e.g., 'account', 'contact')"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "GUID of the record to update (from primary ID field)"
                            },
                            "data": {
                                "type": "object",
                                "description": "Fields to update as dictionary with column names as keys"
                            }
                        },
                        "required": ["table_name", "record_id", "data"]
                    }
                }
            },
        ]
        
        # Prepare messages for the model
        model_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_request.messages
        ]
        
        # Add system message with Dataverse context (loaded from file)
        system_prompt_content = load_system_prompt()
        system_message = {
            "role": "system",
            "content": system_prompt_content
        }
        model_messages.insert(0, system_message)
        
        # Call Databricks Foundation Model
        try:
            response = call_foundation_model(
                model_name=chat_request.model,
                messages=model_messages,
                tools=tools,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
                token=db_token,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calling Databricks Foundation Model: {str(e)}"
            )
        
        # Extract response
        if not response.get('choices') or len(response['choices']) == 0:
            raise HTTPException(
                status_code=500,
                detail="No response from model"
            )
        
        message = response['choices'][0]['message']
        
        # Check if model wants to call tools
        if message.get('tool_calls'):
            tool_results = []
            executed_tools = []
            
            for tool_call in message['tool_calls']:
                tool_name = tool_call['function']['name']
                tool_args = tool_call['function']['arguments']
                
                # Parse arguments if they're a JSON string
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        tool_args = {}
                
                # Execute the tool
                try:
                    if tool_name == "list_tables":
                        result = list_tables_impl(**tool_args)
                    elif tool_name == "describe_table":
                        result = describe_table_impl(**tool_args)
                    elif tool_name == "read_query":
                        result = read_query_impl(**tool_args)
                    elif tool_name == "create_record":
                        result = create_record_impl(**tool_args)
                    elif tool_name == "update_record":
                        result = update_record_impl(**tool_args)
                    else:
                        result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                    # Anthropic Claude format for tool results
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call['id'],
                        "content": json.dumps(result) if isinstance(result, dict) else str(result)
                    })

                    executed_tools.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result
                    })

                except Exception as e:
                    # Tool execution error
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call['id'],
                        "content": json.dumps({"success": False, "error": str(e)})
                    })

                    executed_tools.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": {"success": False, "error": str(e)}
                    })
            
            # Send tool results back to model (Anthropic Claude format)
            # First, add the assistant's message with tool_use blocks
            assistant_msg = {
                "role": "assistant",
                "content": message.get('content') or message['tool_calls']  # Claude needs content
            }

            model_messages.append(assistant_msg)

            # Then add tool results as a user message
            model_messages.append({
                "role": "user",
                "content": tool_results  # Array of tool_result objects
            })
            
            # Get final response from model
            try:
                final_response = call_foundation_model(
                    model_name=chat_request.model,
                    messages=model_messages,
                    tools=tools,
                    temperature=chat_request.temperature,
                    max_tokens=chat_request.max_tokens,
                    token=db_token,
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling Databricks Foundation Model (final): {str(e)}"
                )
            
            if not final_response.get('choices') or len(final_response['choices']) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="No final response from model"
                )
            
            final_message = final_response['choices'][0]['message']
            
            return AgentChatResponse(
                response=final_message.get('content') or "I apologize, but I couldn't generate a response.",
                tool_calls=executed_tools,
                trace_id=None  # TODO: Implement MLflow tracing
            )
        else:
            # No tool calls, just return the response
            return AgentChatResponse(
                response=message.get('content') or "I apologize, but I couldn't generate a response.",
                tool_calls=None,
                trace_id=None
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

