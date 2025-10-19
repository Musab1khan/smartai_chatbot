"""
SmartAI Gateway - Multi-AI Provider Router
Handles 15+ free and paid AI APIs with automatic fallback
"""

import frappe
import requests
import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class AIProviderRegistry:
    """Registry of all supported AI providers"""
    
    PROVIDERS = {
        "openrouter": {
            "name": "OpenRouter",
            "endpoint": "https://api.openrouter.ai/api/v1/chat/completions",
            "models": ["deepseek/deepseek-r1", "openai/gpt-4-turbo", "anthropic/claude-3-sonnet"],
            "free_tier": True,
            "rate_limit": 50,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
            "requires_referer": True,
        },
        "siliconflow": {
            "name": "SiliconFlow",
            "endpoint": "https://api.siliconflow.cn/v1/chat/completions",
            "models": ["deepseek-v3", "qwen/qwen-32b", "meta-llama/llama-3-70b"],
            "free_tier": True,
            "rate_limit": 100,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "huggingface": {
            "name": "Hugging Face",
            "endpoint": "https://api-inference.huggingface.co/v1/chat/completions",
            "models": ["meta-llama/Llama-2-70b-chat-hf", "mistralai/Mistral-7B-Instruct"],
            "free_tier": True,
            "rate_limit": 30,
            "max_tokens": 4096,
            "cost_per_1k_tokens": 0.0,
        },
        "groq": {
            "name": "Groq",
            "endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "models": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
            "free_tier": True,
            "rate_limit": 30,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "github_models": {
            "name": "GitHub Models",
            "endpoint": "https://models.inference.ai.azure.com/chat/completions",
            "models": ["gpt-4o", "llama-3.1-70b", "phi-3.5-mini"],
            "free_tier": True,
            "rate_limit": 15,
            "max_tokens": 4096,
            "cost_per_1k_tokens": 0.0,
        },
        "google_gemini": {
            "name": "Google Gemini",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            "models": ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"],
            "free_tier": True,
            "rate_limit": 60,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
            "is_rest": False,
        },
        "anthropic_claude": {
            "name": "Anthropic Claude",
            "endpoint": "https://api.anthropic.com/v1/messages",
            "models": ["claude-3.5-sonnet", "claude-3-opus", "claude-3-haiku"],
            "free_tier": False,
            "rate_limit": 100,
            "max_tokens": 200000,
            "cost_per_1k_tokens": 0.003,
        },
        "ollama": {
            "name": "Ollama (Local)",
            "endpoint": "http://localhost:11434/v1/chat/completions",
            "models": ["deepseek-r1", "llama2", "neural-chat"],
            "free_tier": True,
            "is_local": True,
            "rate_limit": 1000,
            "max_tokens": 4096,
            "cost_per_1k_tokens": 0.0,
        },
        "coze": {
            "name": "Coze",
            "endpoint": "https://api.coze.com/v3/chat",
            "models": ["gpt-4", "deepseek", "gemini"],
            "free_tier": True,
            "rate_limit": 100,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "together": {
            "name": "Together AI",
            "endpoint": "https://api.together.xyz/v1/chat/completions",
            "models": ["meta-llama/Llama-3-70b", "mistralai/Mistral-7B"],
            "free_tier": True,
            "rate_limit": 60,
            "max_tokens": 4096,
            "cost_per_1k_tokens": 0.0,
        },
        "alibabacloud": {
            "name": "Alibaba Cloud",
            "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
            "free_tier": True,
            "rate_limit": 50,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "nvidiasam": {
            "name": "NVIDIA NIM",
            "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
            "models": ["meta/llama-3.1-405b-instruct", "deepseek-ai/deepseek-coder"],
            "free_tier": True,
            "rate_limit": 60,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "cometapi": {
            "name": "CometAPI",
            "endpoint": "https://api.comet-ai.com/v1/completions",
            "models": ["deepseek", "gpt-4"],
            "free_tier": True,
            "rate_limit": 100,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "vercelai": {
            "name": "Vercel AI",
            "endpoint": "https://api.vercel.ai/v1/chat",
            "models": ["deepseek", "gemini"],
            "free_tier": True,
            "rate_limit": 50,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "sambacloud": {
            "name": "SambaCloud",
            "endpoint": "https://api.sambacloud.ai/v1/chat/completions",
            "models": ["deepseek-v3", "llama-3"],
            "free_tier": True,
            "rate_limit": 100,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
        "llm7": {
            "name": "LLM7",
            "endpoint": "https://api.llm7.com/v1/chat/completions",
            "models": ["deepseek-v3", "gpt-4"],
            "free_tier": True,
            "rate_limit": 50,
            "max_tokens": 8000,
            "cost_per_1k_tokens": 0.0,
        },
    }


class RateLimiter:
    """Advanced rate limiting with distributed cache support"""
    
    def __init__(self):
        self.cache_prefix = "smartai_ratelimit:"
    
    def get_cache_key(self, provider: str, window: str = "minute") -> str:
        """Generate cache key for rate limiting"""
        now = datetime.now()
        if window == "minute":
            timestamp = now.strftime("%Y%m%d%H%M")
        elif window == "hour":
            timestamp = now.strftime("%Y%m%d%H")
        else:  # day
            timestamp = now.strftime("%Y%m%d")
        return f"{self.cache_prefix}{provider}:{timestamp}"
    
    def check_rate_limit(self, provider: str, limit: int) -> Tuple[bool, Dict]:
        """Check if provider is rate limited"""
        key = self.get_cache_key(provider, "minute")
        current_count = frappe.cache().get(key) or 0
        
        return {
            "is_limited": current_count >= limit,
            "current_count": current_count,
            "limit": limit,
            "remaining": max(0, limit - current_count),
        }
    
    def increment(self, provider: str):
        """Increment rate limit counter"""
        key = self.get_cache_key(provider, "minute")
        current = frappe.cache().get(key) or 0
        frappe.cache().set(key, current + 1, ex=60)
    
    def reset(self, provider: str):
        """Reset rate limit counter"""
        key = self.get_cache_key(provider, "minute")
        frappe.cache().delete(key)


class AIGateway:
    """Main AI Gateway for intelligent routing and failover"""
    
    def __init__(self):
        self.registry = AIProviderRegistry()
        self.rate_limiter = RateLimiter()
        self.current_provider = None
    
    @frappe.whitelist()
    def create_session(self, language: str = "English", title: str = None) -> Dict:
        """Create a new chat session"""
        try:
            session = frappe.get_doc({
                "doctype": "Chat Session",
                "user": frappe.session.user,
                "language": language,
                "session_title": title or f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "status": "Active",
            })
            session.insert(ignore_permissions=True)
            
            return {
                "success": True,
                "session_id": session.name,
                "message": "Session created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @frappe.whitelist()
    def chat(self, message: str, session_id: str, language: str = "English",
             attachments: List = None) -> Dict:
        """Main chat endpoint with multi-AI routing"""
        
        try:
            start_time = time.time()
            
            # Validate inputs
            if not message or not message.strip():
                return {"success": False, "error": "Message cannot be empty"}
            
            if not frappe.db.exists("Chat Session", session_id):
                return {"success": False, "error": "Invalid session ID"}
            
            # Process message
            intent, entities = self._extract_intent(message, language)
            
            # Fetch ERPNext context if needed
            erp_context = None
            if intent in ["data_query", "report_generation", "analytics"]:
                erp_context = self._fetch_erp_data(entities, language)
            
            # Get best available provider
            provider_config = self._get_best_provider()
            if not provider_config:
                return {
                    "success": False,
                    "error": "No AI providers available. Please configure at least one."
                }
            
            # Build system prompt
            system_prompt = self._build_system_prompt(language, erp_context)
            
            # Call AI provider
            ai_response = self._call_ai_provider(
                provider_config,
                system_prompt,
                message,
                language
            )
            
            if not ai_response:
                raise Exception("No response from AI provider")
            
            # Process response
            processed_response = self._process_ai_response(
                ai_response, intent, entities, erp_context
            )
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Save to chat history
            self._save_chat_message(
                session_id=session_id,
                role="user",
                content=message,
                language=language,
                intent=intent,
                entities=json.dumps(entities),
            )
            
            self._save_chat_message(
                session_id=session_id,
                role="assistant",
                content=processed_response.get("response"),
                language=language,
                response_time_ms=response_time_ms,
                ai_provider=provider_config.get("provider_name"),
                model_used=provider_config.get("model_name"),
            )
            
            # Log usage
            self._log_usage(
                provider_config.get("provider_name"),
                intent,
                len(message),
                response_time_ms
            )
            
            return {
                "success": True,
                "response": processed_response.get("response"),
                "provider": provider_config.get("provider_name"),
                "model": provider_config.get("model_name"),
                "charts": processed_response.get("charts", []),
                "suggested_actions": processed_response.get("suggested_actions", []),
                "exportable": processed_response.get("exportable", False),
                "response_time_ms": response_time_ms,
            }
        
        except Exception as e:
            logger.error(f"Chat error: {str(e)}", exc_info=True)
            frappe.log_error(f"SmartAI Chat Error: {str(e)}", "AI Gateway Error")
            
            return {
                "success": False,
                "error": str(e),
                "fallback_message": "معافی ہے، کچھ تقنیکی مسئلہ ہے۔ براہ کرم دوبارہ کوشش کریں۔"
            }
    
    def _get_best_provider(self) -> Optional[Dict]:
        """Get best available provider with intelligent selection"""
        
        try:
            # Get active providers
            providers = frappe.db.get_list(
                "AI API Configuration",
                filters={
                    "status": "Active",
                    "docstatus": 0
                },
                fields=["*"],
                order_by="priority asc"
            )
            
            if not providers:
                return None
            
            # Check rate limits and select best
            for provider in providers:
                rate_check = self.rate_limiter.check_rate_limit(
                    provider.provider_name,
                    provider.rate_limit
                )
                
                if not rate_check["is_limited"]:
                    # Convert to dict if needed
                    if hasattr(provider, 'as_dict'):
                        return provider.as_dict()
                    return dict(provider)
            
            # If all rate limited, try fallback providers
            fallback = frappe.db.get_list(
                "AI API Configuration",
                filters={
                    "is_fallback": 1,
                    "status": "Active",
                    "docstatus": 0
                },
                fields=["*"],
                order_by="priority asc",
                limit_page_length=1
            )
            
            if fallback:
                return dict(fallback[0])
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting best provider: {str(e)}")
            return None
    
    def _extract_intent(self, message: str, language: str) -> Tuple[str, Dict]:
        """Extract intent and entities from message"""
        
        intent_keywords = {
            "data_query": [
                "show", "display", "دکھاؤ", "عرض", "tell me", "کہو",
                "list", "get", "فہرست", "حاصل"
            ],
            "report_generation": [
                "report", "رپورٹ", "summary", "خلاصہ",
                "analytics", "analysis", "تجزیہ"
            ],
            "order_creation": [
                "create", "بنائو", "generate", "place",
                "new", "نیا", "order", "آرڈر"
            ],
            "stock_check": [
                "stock", "inventory", "quantity", "اسٹاک",
                "موجودہ", "available", "دستیاب"
            ],
            "customer_info": [
                "customer", "client", "کسٹمر", "گاہک",
                "contact", "رابطہ", "details", "تفصیلات"
            ],
        }
        
        message_lower = message.lower()
        detected_intent = "general_query"
        
        for intent, keywords in intent_keywords.items():
            if any(kw.lower() in message_lower for kw in keywords):
                detected_intent = intent
                break
        
        # Extract entities
        entities = self._extract_entities(message, language)
        
        return detected_intent, entities
    
    def _extract_entities(self, message: str, language: str) -> Dict:
        """Extract named entities from message"""
        import re
        
        entities = {
            "date_range": None,
            "product": None,
            "customer": None,
            "supplier": None,
            "time_period": None,
            "amount": None,
            "status": None,
        }
        
        # Time periods
        time_patterns = {
            "last_month": [
                "last month", "پچھلے مہینے", "الشهر الماضي",
                "last 30 days", "گزشتہ 30 دن"
            ],
            "last_quarter": [
                "last quarter", "سہ ماہی", "الربع الأخير",
                "last 3 months", "گزشتہ 3 مہینے"
            ],
            "last_year": [
                "last year", "گزشتہ سال", "السنة الماضية",
                "last 12 months"
            ],
            "today": [
                "today", "آج", "اليوم"
            ],
            "this_week": [
                "this week", "اس ہفتے", "هذا الأسبوع"
            ],
        }
        
        for period, keywords in time_patterns.items():
            if any(kw.lower() in message.lower() for kw in keywords):
                entities["time_period"] = period
                break
        
        # Amount extraction
        amount_pattern = r'\$[\d,]+|[\d,]+\s*(?:rupees|tk|درہم|ریال|روپے)'
        amounts = re.findall(amount_pattern, message, re.IGNORECASE)
        if amounts:
            entities["amount"] = amounts[0]
        
        return entities
    
    def _fetch_erp_data(self, entities: Dict, language: str) -> Dict:
        """Fetch relevant ERPNext data"""
        
        context = {
            "sales_orders": [],
            "purchase_orders": [],
            "customers": [],
            "suppliers": [],
            "inventory": [],
            "pending_orders": [],
            "summary": {}
        }
        
        try:
            # Fetch based on time period
            time_period = entities.get("time_period", "last_month")
            
            if time_period == "last_month":
                date_from = frappe.utils.add_months(frappe.utils.today(), -1)
            elif time_period == "last_quarter":
                date_from = frappe.utils.add_months(frappe.utils.today(), -3)
            elif time_period == "last_year":
                date_from = frappe.utils.add_months(frappe.utils.today(), -12)
            elif time_period == "today":
                date_from = frappe.utils.today()
            else:
                date_from = frappe.utils.add_months(frappe.utils.today(), -1)
            
            # Sales data
            context["sales_orders"] = frappe.db.get_list(
                "Sales Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ],
                fields=["name", "customer", "grand_total", "status", "creation"],
                limit_page_length=10,
                order_by="creation desc"
            )
            
            # Top customers
            top_customers = frappe.db.sql(f"""
                SELECT customer, COUNT(*) as order_count, SUM(grand_total) as total_sales
                FROM `tabSales Order`
                WHERE DATE(creation) >= DATE('{date_from}')
                AND status != 'Cancelled'
                GROUP BY customer
                ORDER BY total_sales DESC
                LIMIT 5
            """, as_dict=True)
            context["customers"] = top_customers
            
            # Low stock items
            low_stock = frappe.db.get_list(
                "Item",
                filters=[["reorder_level", ">", 0]],
                fields=["item_code", "item_name", "stock_qty", "reorder_level"],
                limit_page_length=5
            )
            context["inventory"] = low_stock
            
            # Pending orders
            pending = frappe.db.get_list(
                "Sales Order",
                filters=[["status", "=", "Open"]],
                fields=["name", "customer", "grand_total"],
                limit_page_length=5
            )
            context["pending_orders"] = pending
            
            # Summary
            total_sales = frappe.db.get_value(
                "Sales Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ],
                fieldname="SUM(grand_total)"
            ) or 0
            
            context["summary"] = {
                "total_sales": total_sales,
                "total_orders": len(context["sales_orders"]),
                "period": time_period,
            }
        
        except Exception as e:
            logger.error(f"Error fetching ERP data: {str(e)}")
        
        return context
    
    def _build_system_prompt(self, language: str, erp_context: Dict = None) -> str:
        """Build intelligent system prompt with context"""
        
        prompts = {
            "Urdu": """تم ایک ذہین ERPNext اسسٹنٹ ہو۔ براہ کرم:
1. صارف کی زبان میں واضح اور مختصر جوابات دیں
2. ERPNext کے ڈیٹا سے درست اور حالیہ معلومات فراہم کریں
3. جب ممکن ہو تو اعداد و شمار اور رپورٹس پیش کریں
4. اگر کوئی اقدام درکار ہو تو تجاویز دیں

موجودہ سسٹم میں دستیاب ڈیٹا:
{erp_data}

براہ مہربانی صارف کے سوال کا درست، مددگار اور کاروباری لحاظ سے متعلقہ جواب دیں۔""",

            "English": """You are an intelligent ERPNext assistant. Please:
1. Provide clear and concise answers in the user's preferred language
2. Use accurate and current data from ERPNext when available
3. Present data with statistics and reports where relevant
4. Suggest helpful actions when appropriate

Current ERPNext Data Available:
{erp_data}

Please provide accurate, helpful, and business-relevant responses to user queries.""",

            "Arabic": """أنت مساعد ذكي في ERPNext. يرجى:
1. تقديم إجابات واضحة وموجزة بلغة المستخدم
2. استخدام البيانات الدقيقة والحالية من ERPNext
3. تقديم الإحصائيات والتقارير عند الإمكان
4. اقتراح إجراءات مفيدة عند الضرورة

البيانات المتاحة في النظام:
{erp_data}

يرجى تقديم إجابات دقيقة ومفيدة ومتعلقة بالأعمال."""
        }
        
        selected_prompt = prompts.get(language, prompts["English"])
        
        # Format with context
        erp_data_str = json.dumps(erp_context or {}, ensure_ascii=False, indent=2) if erp_context else "No data"
        
        return selected_prompt.format(erp_data=erp_data_str[:2000])  # Limit context size
    
    def _call_ai_provider(self, provider_config: Dict, system_prompt: str,
                         user_message: str, language: str) -> Optional[str]:
        """Route request to appropriate AI provider"""
        
        provider_name = provider_config.get("provider_name")
        
        try:
            # Log attempt
            logger.info(f"Calling AI provider: {provider_name}")
            
            # Route to appropriate handler
            if provider_name == "openrouter":
                return self._call_openrouter(provider_config, system_prompt, user_message)
            
            elif provider_name == "siliconflow":
                return self._call_siliconflow(provider_config, system_prompt, user_message)
            
            elif provider_name == "groq":
                return self._call_groq(provider_config, system_prompt, user_message)
            
            elif provider_name == "ollama":
                return self._call_ollama(provider_config, system_prompt, user_message)
            
            elif provider_name == "google_gemini":
                return self._call_google_gemini(provider_config, system_prompt, user_message)
            
            elif provider_name == "huggingface":
                return self._call_huggingface(provider_config, system_prompt, user_message)
            
            elif provider_name == "github_models":
                return self._call_github_models(provider_config, system_prompt, user_message)
            
            elif provider_name == "anthropic_claude":
                return self._call_anthropic(provider_config, system_prompt, user_message)
            
            else:
                # Generic OpenAI-compatible endpoint
                return self._call_generic_openai(provider_config, system_prompt, user_message)
        
        except Exception as e:
            logger.error(f"Error calling {provider_name}: {str(e)}")
            self.rate_limiter.increment(provider_name)
            return None
    
    def _call_openrouter(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {config.get('api_key')}",
            "HTTP-Referer": frappe.utils.get_site_url(),
            "X-Title": "SmartAI Chatbot",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": config.get("model_name", "deepseek/deepseek-r1"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": min(config.get("max_tokens", 2048), 4096),
            "temperature": config.get("temperature", 0.7),
        }
        
        try:
            response = requests.post(
                config.get("api_endpoint"),
                headers=headers,
                json=payload,
                timeout=config.get("timeout_seconds", 30)
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise
    
    def _call_siliconflow(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call SiliconFlow API"""
        headers = {
            "Authorization": f"Bearer {config.get('api_key')}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": config.get("model_name", "deepseek-v3"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": min(config.get("max_tokens", 2048), 4096),
            "temperature": config.get("temperature", 0.7),
        }
        
        try:
            response = requests.post(
                config.get("api_endpoint"),
                headers=headers,
                json=payload,
                timeout=config.get("timeout_seconds", 30)
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"SiliconFlow API error: {str(e)}")
            raise
    
    def _call_groq(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call Groq API (Fastest inference)"""
        headers = {
            "Authorization": f"Bearer {config.get('api_key')}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": config.get("model_name", "llama-3.1-70b-versatile"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": min(config.get("max_tokens", 2048), 4096),
            "temperature": config.get("temperature", 0.7),
        }
        
        try:
            response = requests.post(
                config.get("api_endpoint"),
                headers=headers,
                json=payload,
                timeout=config.get("timeout_seconds", 30)
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    def _call_ollama(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call Local Ollama instance"""
        payload = {
            "model": config.get("model_name", "deepseek-r1"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
        }
        
        try:
            response = requests.post(
                f"{config.get('api_endpoint').rstrip('/')}/chat",
                json=payload,
                timeout=config.get("timeout_seconds", 60)
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama error: {str(e)}")
            raise
    
    def _call_google_gemini(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call Google Gemini API"""
        api_key = config.get('api_key')
        model = config.get('model_name', 'gemini-1.5-flash')
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_prompt}\n\nUser: {user_message}"
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": min(config.get("max_tokens", 2048), 8000),
                "temperature": config.get("temperature", 0.7),
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=config.get("timeout_seconds", 30))
            response.raise_for_status()
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Gemini error: {str(e)}")
            raise
    
    def _call_huggingface(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call Hugging Face Inference API"""
        headers = {
            "Authorization": f"Bearer {config.get('api_key')}",
        }
        
        payload = {
            "inputs": f"{system_prompt}\n\nUser: {user_message}",
        }
        
        try:
            response = requests.post(
                config.get("api_endpoint"),
                headers=headers,
                json=payload,
                timeout=config.get("timeout_seconds", 30)
            )
            response.raise_for_status()
            
            result = response.json()
            return result[0]["generated_text"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face error: {str(e)}")
            raise
    
    def _call_github_models(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call GitHub Models via Azure Inference"""
        headers = {
            "Authorization": f"Bearer {config.get('api_key')}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "model": config.get("model_name", "gpt-4o"),
            "temperature": config.get("temperature", 0.7),
            "max_tokens": min(config.get("max_tokens", 2048), 4096),
        }
        
        try:
            response = requests.post(
                config.get("api_endpoint"),
                headers=headers,
                json=payload,
                timeout=config.get("timeout_seconds", 30)
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub Models error: {str(e)}")
            raise
    
    def _call_anthropic(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call Anthropic Claude API"""
        headers = {
            "x-api-key": config.get('api_key'),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        payload = {
            "model": config.get("model_name", "claude-3.5-sonnet"),
            "max_tokens": min(config.get("max_tokens", 2048), 200000),
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }
        
        try:
            response = requests.post(
                config.get("api_endpoint"),
                headers=headers,
                json=payload,
                timeout=config.get("timeout_seconds", 30)
            )
            response.raise_for_status()
            
            result = response.json()
            return result["content"][0]["text"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Anthropic error: {str(e)}")
            raise
    
    def _call_generic_openai(self, config: Dict, system_prompt: str, user_message: str) -> str:
        """Call generic OpenAI-compatible endpoint"""
        headers = {
            "Authorization": f"Bearer {config.get('api_key')}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": config.get("model_name"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": min(config.get("max_tokens", 2048), 4096),
            "temperature": config.get("temperature", 0.7),
        }
        
        try:
            response = requests.post(
                config.get("api_endpoint"),
                headers=headers,
                json=payload,
                timeout=config.get("timeout_seconds", 30)
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Generic OpenAI error: {str(e)}")
            raise
    
    def _process_ai_response(self, response: str, intent: str, 
                            entities: Dict, erp_context: Dict = None) -> Dict:
        """Process AI response and generate visualizations"""
        
        result = {
            "response": response,
            "charts": [],
            "suggested_actions": [],
            "exportable": False,
        }
        
        # Generate visualizations for analytical queries
        if intent in ["analytics", "report_generation"]:
            result["charts"] = self._generate_charts(intent, erp_context)
            result["exportable"] = True
            result["suggested_actions"] = [
                {"action": "Export as Excel", "icon": "download"},
                {"action": "Export as PDF", "icon": "file-pdf"},
                {"action": "Send via Email", "icon": "envelope"},
                {"action": "Schedule Report", "icon": "clock"},
            ]
        
        elif intent == "data_query":
            result["suggested_actions"] = [
                {"action": "Create Report", "icon": "chart-bar"},
                {"action": "Export Data", "icon": "download"},
            ]
        
        return result
    
    def _generate_charts(self, intent: str, erp_context: Dict) -> List:
        """Generate chart configurations"""
        charts = []
        
        if not erp_context:
            return charts
        
        try:
            # Sales trend chart
            if erp_context.get("sales_orders"):
                charts.append({
                    "type": "line",
                    "title": "Sales Trend",
                    "data": {
                        "labels": [so["name"][:10] for so in erp_context["sales_orders"][:10]],
                        "datasets": [{
                            "label": "Sales Amount",
                            "data": [so.get("grand_total", 0) for so in erp_context["sales_orders"][:10]],
                        }]
                    }
                })
            
            # Top customers pie chart
            if erp_context.get("customers"):
                charts.append({
                    "type": "pie",
                    "title": "Top Customers",
                    "data": {
                        "labels": [c.get("customer", "N/A") for c in erp_context["customers"]],
                        "datasets": [{
                            "data": [c.get("total_sales", 0) for c in erp_context["customers"]],
                        }]
                    }
                })
        
        except Exception as e:
            logger.error(f"Error generating charts: {str(e)}")
        
        return charts
    
    def _save_chat_message(self, session_id: str, role: str, content: str,
                          language: str, intent: str = None, entities: str = None,
                          response_time_ms: float = None, ai_provider: str = None,
                          model_used: str = None):
        """Save message to database"""
        try:
            msg = frappe.get_doc({
                "doctype": "Chat Message",
                "chat_session": session_id,
                "role": role,
                "content": content,
                "language": language,
                "intent": intent,
                "entities": entities,
                "response_time_ms": response_time_ms,
                "ai_provider_used": ai_provider,
                "model_used": model_used,
            })
            msg.insert(ignore_permissions=True)
        
        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")
    
    def _log_usage(self, provider: str, intent: str, input_length: int,
                  response_time_ms: float):
        """Log AI usage for analytics"""
        try:
            frappe.get_doc({
                "doctype": "AI Usage Log",
                "provider_name": provider,
                "intent": intent,
                "input_length": input_length,
                "response_time_ms": response_time_ms,
                "timestamp": frappe.utils.now(),
            }).insert(ignore_permissions=True)
        
        except Exception as e:
            logger.error(f"Error logging usage: {str(e)}")


# Public API endpoints
@frappe.whitelist()
def chat(message, session_id, language="English", attachments=None):
    """Public chat endpoint"""
    gateway = AIGateway()
    return gateway.chat(message, session_id, language, attachments)


@frappe.whitelist()
def create_session(language="English", title=None):
    """Create new chat session"""
    gateway = AIGateway()
    return gateway.create_session(language, title)
