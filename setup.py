"""
SmartAI Setup Script - Initialize configuration and create default providers
"""

import frappe
from frappe.utils import get_site_url
import logging

logger = logging.getLogger(__name__)


def setup_providers():
    """Create default AI provider configurations"""
    
    default_providers = [
        {
            "provider_name": "OpenRouter",
            "model_name": "deepseek/deepseek-r1",
            "api_endpoint": "https://api.openrouter.ai/api/v1/chat/completions",
            "rate_limit": 50,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 1,
            "is_fallback": 0,
        },
        {
            "provider_name": "SiliconFlow",
            "model_name": "deepseek-v3",
            "api_endpoint": "https://api.siliconflow.cn/v1/chat/completions",
            "rate_limit": 100,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 2,
            "is_fallback": 0,
        },
        {
            "provider_name": "Groq",
            "model_name": "llama-3.1-70b-versatile",
            "api_endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "rate_limit": 30,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 3,
            "is_fallback": 0,
        },
        {
            "provider_name": "Ollama",
            "model_name": "deepseek-r1",
            "api_endpoint": "http://localhost:11434/v1/chat/completions",
            "rate_limit": 1000,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 10,
            "is_fallback": 1,
            "is_local": 1,
        },
        {
            "provider_name": "Google Gemini",
            "model_name": "gemini-1.5-flash",
            "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            "rate_limit": 60,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 4,
            "is_fallback": 0,
        },
        {
            "provider_name": "Hugging Face",
            "model_name": "meta-llama/Llama-2-70b-chat-hf",
            "api_endpoint": "https://api-inference.huggingface.co/v1/chat/completions",
            "rate_limit": 30,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 5,
            "is_fallback": 0,
        },
        {
            "provider_name": "GitHub Models",
            "model_name": "gpt-4o",
            "api_endpoint": "https://models.inference.ai.azure.com/chat/completions",
            "rate_limit": 15,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 6,
            "is_fallback": 0,
        },
        {
            "provider_name": "Anthropic Claude",
            "model_name": "claude-3.5-sonnet",
            "api_endpoint": "https://api.anthropic.com/v1/messages",
            "rate_limit": 100,
            "max_tokens": 4096,
            "temperature": 0.7,
            "status": "Inactive",
            "priority": 7,
            "is_fallback": 0,
        },
    ]
    
    for provider in default_providers:
        try:
            if not frappe.db.exists("AI API Configuration", provider["provider_name"]):
                doc = frappe.get_doc({
                    "doctype": "AI API Configuration",
                    **provider
                })
                doc.insert(ignore_permissions=True)
                logger.info(f"Created provider: {provider['provider_name']}")
        except Exception as e:
            logger.error(f"Error creating provider {provider['provider_name']}: {str(e)}")


def create_custom_doctypes():
    """Create necessary custom DocTypes if they don't exist"""
    
    doctypes_to_create = [
        {
            "name": "AI Usage Log",
            "module": "SmartAI Chatbot",
            "document_type": "DocType",
            "fields": [
                {"fieldname": "provider_name", "fieldtype": "Data", "label": "Provider Name"},
                {"fieldname": "intent", "fieldtype": "Data", "label": "Intent"},
                {"fieldname": "input_length", "fieldtype": "Int", "label": "Input Length"},
                {"fieldname": "response_time_ms", "fieldtype": "Float", "label": "Response Time (ms)"},
                {"fieldname": "timestamp", "fieldtype": "Datetime", "label": "Timestamp"},
                {"fieldname": "tokens_used", "fieldtype": "Int", "label": "Tokens Used"},
                {"fieldname": "cost_usd", "fieldtype": "Currency", "label": "Cost (USD)"},
            ]
        },
        {
            "name": "Autonomous Action",
            "module": "SmartAI Chatbot",
            "document_type": "DocType",
            "fields": [
                {"fieldname": "action_type", "fieldtype": "Select", "label": "Action Type", "options": "create_sales_order\ncreate_purchase_order\nsend_email\ncreate_customer"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nProcessing\nCompleted\nFailed", "default": "Pending"},
                {"fieldname": "data", "fieldtype": "Code", "label": "Data (JSON)", "options": "json"},
                {"fieldname": "result", "fieldtype": "Text", "label": "Result"},
                {"fieldname": "error_message", "fieldtype": "Text", "label": "Error Message"},
            ]
        },
        {
            "name": "AI Training Data",
            "module": "SmartAI Chatbot",
            "document_type": "DocType",
            "fields": [
                {"fieldname": "user_input", "fieldtype": "Text", "label": "User Input"},
                {"fieldname": "ai_response", "fieldtype": "Text", "label": "AI Response"},
                {"fieldname": "feedback", "fieldtype": "Select", "label": "Feedback", "options": "Correct\nIncorrect\nPartial\nNeutral"},
                {"fieldname": "corrected_response", "fieldtype": "Text", "label": "Corrected Response"},
                {"fieldname": "category", "fieldtype": "Data", "label": "Category"},
            ]
        },
    ]
    
    for doctype in doctypes_to_create:
        try:
            if not frappe.db.exists("DocType", doctype["name"]):
                doc = frappe.get_doc({
                    "doctype": "DocType",
                    **doctype
                })
                doc.insert(ignore_permissions=True)
                logger.info(f"Created DocType: {doctype['name']}")
        except Exception as e:
            logger.error(f"Error creating DocType {doctype['name']}: {str(e)}")


def create_workspace():
    """Create SmartAI workspace"""
    try:
        if not frappe.db.exists("Workspace", "SmartAI Chatbot"):
            workspace = frappe.get_doc({
                "doctype": "Workspace",
                "name": "SmartAI Chatbot",
                "label": "SmartAI Chatbot",
                "is_default": 0,
                "sidebar_items": [
                    {
                        "type": "Link",
                        "label": "Chat",
                        "link": "/app/smartai-chat",
                    },
                    {
                        "type": "Link",
                        "label": "Chat Sessions",
                        "link": "/app/chat-session",
                    },
                    {
                        "type": "Link",
                        "label": "AI Configuration",
                        "link": "/app/ai-api-configuration",
                    },
                    {
                        "type": "Link",
                        "label": "Usage Logs",
                        "link": "/app/ai-usage-log",
                    },
                ]
            })
            workspace.insert(ignore_permissions=True)
            logger.info("Created workspace: SmartAI Chatbot")
    except Exception as e:
        logger.error(f"Error creating workspace: {str(e)}")


def setup_all():
    """Run all setup tasks"""
    logger.info("=== SmartAI Setup Started ===")
    
    setup_providers()
    create_custom_doctypes()
    create_workspace()
    
    logger.info("=== SmartAI Setup Completed ===")
    
    return {
        "success": True,
        "message": "SmartAI Chatbot setup completed successfully!",
        "next_steps": [
            "Configure AI API keys in 'AI API Configuration'",
            "Test each provider connection",
            "Navigate to '/app/smartai-chat' to start chatting",
        ]
    }
