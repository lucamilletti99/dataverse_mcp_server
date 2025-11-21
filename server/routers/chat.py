"""Chat router - provides model selection for Dataverse MCP chat."""

from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()


@router.get('/models')
async def list_available_models() -> Dict[str, Any]:
    """List available Databricks Foundation Models for the chat interface.
    
    Returns list of models that can be used with Dataverse MCP tools.
    """
    # Databricks Foundation Models - sorted by tool support, then alphabetically
    models = [
        # ========================================================================
        # TOOL-ENABLED MODELS (sorted alphabetically)
        # ========================================================================
        
        {
            'id': 'databricks-claude-3.7-sonnet',
            'name': 'Claude 3.7 Sonnet',
            'provider': 'Anthropic',
            'supports_tools': True,
            'context_window': 200000,
            'type': 'chat'
        },
        {
            'id': 'databricks-claude-sonnet-4',
            'name': 'Claude Sonnet 4',
            'provider': 'Anthropic',
            'supports_tools': True,
            'context_window': 200000,
            'type': 'chat'
        },
        {
            'id': 'databricks-claude-sonnet-4-5',
            'name': 'Claude Sonnet 4.5',
            'provider': 'Anthropic',
            'supports_tools': True,
            'context_window': 200000,
            'type': 'chat'
        },
        {
            'id': 'databricks-dbrx-instruct',
            'name': 'DBRX Instruct',
            'provider': 'Databricks',
            'supports_tools': True,
            'context_window': 32768,
            'type': 'chat'
        },
        {
            'id': 'databricks-gemma-3-12b',
            'name': 'Gemma 3 12B',
            'provider': 'Google',
            'supports_tools': True,
            'context_window': 8192,
            'type': 'chat'
        },
        {
            'id': 'databricks-gemini-2-5-flash',
            'name': 'Gemini 2.5 Flash',
            'provider': 'Google',
            'supports_tools': True,
            'context_window': 1000000,
            'type': 'chat'
        },
        {
            'id': 'databricks-gemini-2-5-pro',
            'name': 'Gemini 2.5 Pro',
            'provider': 'Google',
            'supports_tools': True,
            'context_window': 2000000,
            'type': 'chat'
        },
        {
            'id': 'databricks-gpt-5',
            'name': 'GPT-5',
            'provider': 'OpenAI',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-gpt-5-1',
            'name': 'GPT-5.1',
            'provider': 'OpenAI',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-gpt-5-mini',
            'name': 'GPT-5 Mini',
            'provider': 'OpenAI',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-gpt-5-nano',
            'name': 'GPT-5 Nano',
            'provider': 'OpenAI',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-gpt-oss-120b',
            'name': 'GPT OSS 120B',
            'provider': 'OpenAI',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-gpt-oss-20b',
            'name': 'GPT OSS 20B',
            'provider': 'OpenAI',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-meta-llama-3-1-405b-instruct',
            'name': 'Llama 3.1 405B Instruct',
            'provider': 'Meta',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-meta-llama-3-1-70b-instruct',
            'name': 'Llama 3.1 70B Instruct',
            'provider': 'Meta',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-meta-llama-3-2-1b-instruct',
            'name': 'Llama 3.2 1B Instruct',
            'provider': 'Meta',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-meta-llama-3-2-3b-instruct',
            'name': 'Llama 3.2 3B Instruct',
            'provider': 'Meta',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-meta-llama-3-3-70b-instruct',
            'name': 'Llama 3.3 70B Instruct',
            'provider': 'Meta',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-llama-4-maverick',
            'name': 'Llama 4 Maverick (Preview)',
            'provider': 'Meta',
            'supports_tools': True,
            'context_window': 128000,
            'type': 'chat'
        },
        {
            'id': 'databricks-mixtral-8x7b-instruct',
            'name': 'Mixtral 8x7B Instruct',
            'provider': 'Mistral AI',
            'supports_tools': True,
            'context_window': 32768,
            'type': 'chat'
        },
        
        # ========================================================================
        # NOT TOOL-ENABLED MODELS (sorted alphabetically)
        # ========================================================================
        
        {
            'id': 'databricks-claude-opus-4',
            'name': 'Claude Opus 4',
            'provider': 'Anthropic',
            'supports_tools': False,
            'context_window': 200000,
            'type': 'chat'
        },
        {
            'id': 'databricks-claude-opus-4-1',
            'name': 'Claude Opus 4.1',
            'provider': 'Anthropic',
            'supports_tools': False,
            'context_window': 200000,
            'type': 'chat'
        },
        {
            'id': 'databricks-meta-llama-3-1-8b-instruct',
            'name': 'Llama 3.1 8B Instruct',
            'provider': 'Meta',
            'supports_tools': False,
            'context_window': 128000,
            'type': 'chat'
        },
    ]
    
    return {
        'models': models,
        'default': 'databricks-claude-sonnet-4'
    }

