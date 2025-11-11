"""Agent chat router for Dataverse MCP server - with agentic loop."""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from server.trace_storage import get_trace_storage

router = APIRouter()


def load_system_prompt() -> str:
    """Load the Dataverse agent system prompt from markdown file."""
    prompt_file = Path(__file__).parent.parent.parent / "prompts" / "dataverse_agent_system.md"

    try:
        return prompt_file.read_text()
    except Exception as e:
        print(f"⚠️  Could not load system prompt from {prompt_file}: {e}")
        return (
            "You are a Dataverse AI assistant with access to Microsoft Dataverse data.\n\n"
            "## Available Tools:\n"
            "1. **list_tables** - Discover available tables (entities)\n"
            "2. **describe_table** - Get schema/columns for a specific table\n"
            "3. **read_query** - Query records using OData\n"
            "4. **create_record** - Insert new records\n"
            "5. **update_record** - Modify existing records\n\n"
            "Always use the available tools to access real data - never make up information!"
        )


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class AgentChatRequest(BaseModel):
    """Agent chat request model."""
    messages: List[ChatMessage]
    model: str = "databricks-claude-sonnet-4"
    max_tokens: Optional[int] = 2048
    temperature: Optional[float] = 0.7


class AgentChatResponse(BaseModel):
    """Agent chat response model."""
    response: str
    trace_id: Optional[str] = None
    iterations: int = 0


def get_databricks_token(request: Request) -> str:
    """Get Databricks token, prioritizing OBO token."""
    obo_token = request.headers.get('X-Forwarded-Access-Token')
    if obo_token:
        return obo_token

    # Fallback to PAT
    pat = os.environ.get('DATABRICKS_TOKEN')
    if not pat:
        raise HTTPException(status_code=401, detail="No authentication token available")
    return pat


def call_foundation_model(
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
    model: str,
    temperature: float,
    max_tokens: int,
    token: str,
) -> Dict[str, Any]:
    """Call Databricks Foundation Model API."""
    host = os.environ.get('DATABRICKS_HOST', '')

    if not host.startswith('http://') and not host.startswith('https://'):
        host = f'https://{host}'
    host = host.rstrip('/')

    url = f"{host}/serving-endpoints/{model}/invocations"

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

    print(f"🔍 Foundation Model Request: {len(messages)} messages, {len(tools)} tools")
    for i, msg in enumerate(messages):
        role = msg.get('role')
        content_preview = str(msg.get('content', ''))[:80] if msg.get('content') else '[no content]'
        has_tool_calls = 'tool_calls' in msg
        has_tool_call_id = 'tool_call_id' in msg
        print(f"  [{i+1}] role={role}, has_tool_calls={has_tool_calls}, has_tool_call_id={has_tool_call_id}, content={content_preview}")

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
        raise Exception(f"Request error: {str(e)}")


def execute_tool(tool_name: str, tool_args: Dict[str, Any], request: Request) -> str:
    """Execute a Dataverse tool."""
    from server.dataverse_tools import (
        list_tables_impl,
        describe_table_impl,
        read_query_impl,
        create_record_impl,
        update_record_impl,
    )

    print(f"🔧 Executing tool: {tool_name} with args: {tool_args}")

    try:
        if tool_name == "list_tables":
            result = list_tables_impl(
                filter_query=tool_args.get("filter_query"),
                top=tool_args.get("top", 100),
                custom_only=tool_args.get("custom_only", False),
                request=request
            )
        elif tool_name == "describe_table":
            result = describe_table_impl(
                table_name=tool_args["table_name"],
                request=request
            )
        elif tool_name == "read_query":
            result = read_query_impl(
                table_name=tool_args["table_name"],
                select=tool_args.get("select"),
                filter_query=tool_args.get("filter"),
                top=tool_args.get("top", 10),
                orderby=tool_args.get("orderby"),
                request=request
            )
        elif tool_name == "create_record":
            result = create_record_impl(
                table_name=tool_args["table_name"],
                data=tool_args["data"],
                request=request
            )
        elif tool_name == "update_record":
            result = update_record_impl(
                table_name=tool_args["table_name"],
                record_id=tool_args["record_id"],
                data=tool_args["data"],
                request=request
            )
        else:
            return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})

        return json.dumps(result) if isinstance(result, dict) else str(result)
    except Exception as e:
        print(f"❌ Tool execution error: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})


async def run_agent_loop(
    user_messages: List[Dict[str, str]],
    model: str,
    tools: List[Dict[str, Any]],
    temperature: float,
    max_tokens: int,
    request: Request,
    trace_id: str,
    max_iterations: int = 10
) -> Dict[str, Any]:
    """Run the agentic loop - handles tool calling internally."""
    trace_storage = get_trace_storage()

    # Load system prompt
    system_prompt = load_system_prompt()

    # Prepend system message
    messages = [{"role": "system", "content": system_prompt}] + user_messages.copy()

    # Get token for API calls
    token = get_databricks_token(request)

    # Create agent span
    agent_span_id = trace_storage.add_span(
        trace_id=trace_id,
        span_type="AGENT",
        name="Agent Chat",
        inputs={"user_question": user_messages[-1]['content'] if user_messages else ""}
    )

    iteration = 0

    for iteration in range(max_iterations):
        print(f"\n{'='*60}")
        print(f"🔄 Agent Iteration {iteration + 1}/{max_iterations}")
        print(f"{'='*60}")

        # Add LLM span
        llm_span_id = trace_storage.add_span(
            trace_id=trace_id,
            span_type="LLM",
            name=f"llm/serving-endpoints/{model}/invocations",
            inputs={"iteration": iteration + 1, "message_count": len(messages)},
            parent_id=agent_span_id
        )

        try:
            # Call model
            response = call_foundation_model(
                messages=messages,
                tools=tools,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                token=token
            )

            # Complete LLM span
            trace_storage.complete_span(
                trace_id=trace_id,
                span_id=llm_span_id,
                outputs={"response_keys": list(response.keys())},
                status="OK"
            )
        except Exception as e:
            trace_storage.complete_span(
                trace_id=trace_id,
                span_id=llm_span_id,
                outputs={"error": str(e)},
                status="ERROR"
            )
            raise HTTPException(status_code=500, detail=f"Model call failed: {str(e)}")

        # Extract response
        if 'choices' not in response or len(response['choices']) == 0:
            raise HTTPException(status_code=500, detail="No response from model")

        choice = response['choices'][0]
        message = choice.get('message', {})
        finish_reason = choice.get('finish_reason', 'unknown')

        print(f"📤 Model response - finish_reason: {finish_reason}")

        # Check for tool calls
        tool_calls = message.get('tool_calls')

        if not tool_calls:
            # No tools to call - final response
            final_content = message.get('content', '')
            print(f"✅ Final response (no tool calls)")

            # Complete agent span
            trace_storage.complete_span(
                trace_id=trace_id,
                span_id=agent_span_id,
                outputs={"response": final_content, "iterations": iteration + 1},
                status="OK"
            )

            # Complete trace
            trace_storage.complete_trace(trace_id, status="OK")

            return {
                "response": final_content,
                "iterations": iteration + 1
            }

        # Has tool calls - add assistant message and execute tools
        print(f"🔧 Model wants to call {len(tool_calls)} tool(s)")

        # Add assistant message with tool_calls
        assistant_msg = {
            "role": "assistant",
            "tool_calls": tool_calls
        }
        if message.get('content'):
            assistant_msg["content"] = message['content']

        messages.append(assistant_msg)

        # Execute each tool and add results
        for tool_call in tool_calls:
            tool_name = tool_call['function']['name']
            tool_args = json.loads(tool_call['function']['arguments'])
            tool_id = tool_call['id']

            # Add tool span
            tool_span_id = trace_storage.add_span(
                trace_id=trace_id,
                span_type="TOOL",
                name=tool_name,
                inputs=tool_args,
                parent_id=llm_span_id
            )

            try:
                # Execute tool
                result = execute_tool(tool_name, tool_args, request)

                # Complete tool span
                trace_storage.complete_span(
                    trace_id=trace_id,
                    span_id=tool_span_id,
                    outputs={"result": result[:500] if len(result) > 500 else result},
                    status="OK"
                )
            except Exception as e:
                result = json.dumps({"success": False, "error": str(e)})
                trace_storage.complete_span(
                    trace_id=trace_id,
                    span_id=tool_span_id,
                    outputs={"error": str(e)},
                    status="ERROR"
                )

            # Add tool result message
            messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "content": result
            })

    # Hit max iterations
    print(f"⚠️  Reached max iterations ({max_iterations})")
    final_response = "I apologize, but I've reached the maximum number of processing steps. Please try rephrasing your question."

    trace_storage.complete_span(
        trace_id=trace_id,
        span_id=agent_span_id,
        outputs={"response": final_response, "iterations": max_iterations, "status": "max_iterations"},
        status="OK"
    )
    trace_storage.complete_trace(trace_id, status="OK")

    return {
        "response": final_response,
        "iterations": max_iterations
    }


@router.post("/message", response_model=AgentChatResponse)
async def agent_chat(chat_request: AgentChatRequest, request: Request):
    """Agent chat endpoint - runs full agentic loop server-side."""

    # Create trace
    trace_id = str(uuid.uuid4())
    trace_storage = get_trace_storage()
    user_message = chat_request.messages[-1].content if chat_request.messages else ""
    trace_storage.create_trace(trace_id, user_message.strip())

    # Define tools
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
                "description": "Query records from a Dataverse table using simple OData syntax. Retrieve data with optional filtering, sorting, and column selection.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Logical name of the table to query"
                        },
                        "select": {
                            "type": "string",
                            "description": "Comma-separated list of columns to retrieve (e.g., 'name,emailaddress1')"
                        },
                        "filter": {
                            "type": "string",
                            "description": "OData filter expression (e.g., 'name eq \\'Contoso\\'')"
                        },
                        "top": {
                            "type": "integer",
                            "description": "Maximum number of records to return (default: 10)"
                        },
                        "orderby": {
                            "type": "string",
                            "description": "Column to sort by with optional 'asc' or 'desc' (e.g., 'createdon desc')"
                        }
                    },
                    "required": ["table_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_record",
                "description": "Create a new record in a Dataverse table.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Logical name of the table"
                        },
                        "data": {
                            "type": "object",
                            "description": "Record data as key-value pairs"
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
                "description": "Update an existing record in a Dataverse table.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Logical name of the table"
                        },
                        "record_id": {
                            "type": "string",
                            "description": "GUID of the record to update"
                        },
                        "data": {
                            "type": "object",
                            "description": "Record data to update as key-value pairs"
                        }
                    },
                    "required": ["table_name", "record_id", "data"]
                }
            }
        },
    ]

    try:
        # Convert Pydantic messages to dicts
        user_messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]

        # Run agent loop
        result = await run_agent_loop(
            user_messages=user_messages,
            model=chat_request.model,
            tools=tools,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            request=request,
            trace_id=trace_id,
            max_iterations=10
        )

        return AgentChatResponse(
            response=result['response'],
            trace_id=trace_id,
            iterations=result['iterations']
        )

    except HTTPException:
        raise
    except Exception as e:
        # Complete trace with error
        trace_storage.complete_trace(trace_id, status="ERROR")
        raise HTTPException(status_code=500, detail=str(e))
