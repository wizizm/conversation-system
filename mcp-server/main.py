#!/usr/bin/env python3
"""
Enhanced MCP Server with SSE Transport
Compatible with Cursor and other MCP clients supporting SSE
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ENHANCED API CLIENT ===

class EnhancedConversationAPI:
    """增强的API客户端，支持智能压缩和适应性上下文"""
    
    def __init__(self, base_url: str = "http://conversation_app:9000"):
        self.base_url = base_url.rstrip('/')
        # 配置更稳定的HTTP客户端
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=5),
            transport=httpx.AsyncHTTPTransport(retries=3)
        )
        logger.info(f"🔗 Enhanced API client initialized: {base_url}")
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查API"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    async def record_conversation(self, user_msg: str, assistant_msg: str, 
                                topics: List[str] = None, keywords: List[str] = None) -> Dict[str, Any]:
        """记录增强对话"""
        try:
            payload = {
                "role": "user",
                "content": user_msg,
                "topics": topics or [],
                "keywords": keywords or []
            }
            
            # Save user message
            user_response = await self.client.post(f"{self.base_url}/messages", json=payload)
            user_response.raise_for_status()
            
            # Save assistant message
            payload["role"] = "assistant"
            payload["content"] = assistant_msg
            
            assistant_response = await self.client.post(f"{self.base_url}/messages", json=payload)
            assistant_response.raise_for_status()
            
            return {
                "user_message_id": user_response.json().get("message_id"),
                "assistant_message_id": assistant_response.json().get("message_id"),
                "compression_ratio": assistant_response.json().get("compression_ratio", 0),
                "bytes_saved": assistant_response.json().get("bytes_saved", 0),
                "status": "saved"
            }
        except httpx.TimeoutException as e:
            logger.error(f"API timeout error: {e}")
            raise Exception(f"API request timeout: {e}")
        except httpx.ConnectError as e:
            logger.error(f"API connection error: {e}")
            raise Exception(f"Cannot connect to API service: {e}")
        except Exception as e:
            logger.error(f"Error recording enhanced conversation: {e}")
            raise

    async def get_analytics(self) -> Dict[str, Any]:
        """获取增强分析数据"""
        try:
            response = await self.client.get(f"{self.base_url}/analytics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            raise

    async def get_context(self, limit: int = 5, detail_level: str = "medium", format_type: str = "narrative") -> Dict[str, Any]:
        """获取适应性上下文"""
        try:
            payload = {
                "limit": limit,
                "detail_level": detail_level,
                "format_type": format_type
            }
            response = await self.client.post(f"{self.base_url}/context", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            raise

    async def search_conversations(self, query_terms: List[str], limit: int = 10, search_scope: str = "all") -> List[Dict[str, Any]]:
        """搜索会话增强版"""
        try:
            payload = {
                "query_terms": query_terms,
                "limit": limit,
                "search_scope": search_scope
            }
            response = await self.client.post(f"{self.base_url}/search", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            raise

    async def save_message(self, role: str, content: str, topics: List[str] = None, keywords: List[str] = None) -> Dict[str, Any]:
        """保存消息增强版"""
        try:
            payload = {
                "role": role,
                "content": content,
                "topics": topics or [],
                "keywords": keywords or []
            }
            response = await self.client.post(f"{self.base_url}/messages", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise

    async def analyze_compression(self, text: str) -> Dict[str, Any]:
        """压缩分析"""
        try:
            payload = {"text": text}
            response = await self.client.post(f"{self.base_url}/analyze-compression", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error analyzing compression: {e}")
            raise

    async def save_insight(self, insight_type: str, content: str, summary: str = "", 
                          source_messages: List[str] = None, relevance_score: float = 0.8,
                          business_area: str = "", impact_level: str = "medium",
                          actionable_items: List[str] = None) -> str:
        """保存洞察增强版"""
        try:
            payload = {
                "insight_type": insight_type,
                "content": content,
                "summary": summary,
                "source_messages": source_messages or [],
                "relevance_score": relevance_score,
                "business_area": business_area,
                "impact_level": impact_level,
                "actionable_items": actionable_items or []
            }
            response = await self.client.post(f"{self.base_url}/insights", json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("insight_id", "")
        except Exception as e:
            logger.error(f"Error saving insight: {e}")
            raise

# Initialize enhanced API client
api = EnhancedConversationAPI(
    base_url=os.getenv("CONVERSATION_API_URL", "http://conversation_app:9000")
)

# === MCP TOOL IMPLEMENTATIONS ===

async def record_current_conversation(user_message: str, assistant_message: str, 
                                   topics: Optional[List[str]] = None, 
                                   keywords: Optional[List[str]] = None) -> str:
    """记录当前对话交换，支持智能压缩"""
    try:
        result = await api.record_conversation(
            user_msg=user_message,
            assistant_msg=assistant_message,
            topics=topics or [],
            keywords=keywords or []
        )
        
        compression_ratio = result.get('compression_ratio', 0)
        bytes_saved = result.get('bytes_saved', 0)
        
        response = f"✅ Enhanced conversation recorded successfully!\n\n"
        response += f"📊 Compression Statistics:\n"
        response += f"  • Compression Ratio: {compression_ratio:.1%}\n"
        response += f"  • Bytes Saved: {bytes_saved:,}\n"
        response += f"  • Smart Features: ✅ Adaptive Context, ✅ Multi-layer Summary\n"
        
        if result.get('technical_terms'):
            response += f"  • Technical Terms Extracted: {len(result['technical_terms'])}\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error recording conversation: {e}")
        return f"❌ Failed to record conversation: {str(e)}"

async def get_analytics_tool() -> str:
    """获取系统分析数据和统计信息"""
    try:
        analytics = await api.get_analytics()
        
        total_messages = analytics.get('total_messages', 0)
        compression_stats = analytics.get('compression_stats', {})
        tech_terms = analytics.get('technical_terms', [])
        
        response = f"📊 System Analytics Report\n\n"
        response += f"📈 Total Messages: {total_messages:,}\n"
        
        if compression_stats:
            total_saved = compression_stats.get('total_bytes_saved', 0)
            avg_ratio = compression_stats.get('average_compression_ratio', 1.0)
            response += f"💾 Total Bytes Saved: {total_saved:,}\n"
            response += f"📉 Average Compression: {(1-avg_ratio)*100:.1f}%\n"
        
        if tech_terms:
            response += f"🔧 Technical Terms Indexed: {len(tech_terms)}\n"
            response += f"   Top terms: {', '.join(tech_terms[:5])}\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return f"❌ Failed to get analytics: {str(e)}"

async def get_context_tool(limit: int = 5, detail_level: str = "medium", format_type: str = "narrative") -> str:
    """获取适应性上下文信息"""
    try:
        context = await api.get_context(limit=limit, detail_level=detail_level, format_type=format_type)
        
        context_text = context.get('context', '')
        compression_stats = context.get('compression_stats', {})
        
        response = f"🔍 Context Retrieved (Detail: {detail_level})\n\n"
        response += f"📄 Context Length: {len(context_text)} characters\n"
        
        if compression_stats.get('detail_level_used'):
            response += f"🎯 Detail Level Used: {compression_stats['detail_level_used']}\n"
        
        response += f"\n📝 Context:\n{context_text[:500]}..."
        if len(context_text) > 500:
            response += f"\n\n(Showing first 500 characters of {len(context_text)} total)"
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        return f"❌ Failed to get context: {str(e)}"

async def search_conversations_tool(query_terms: List[str], limit: int = 10, search_scope: str = "all") -> str:
    """搜索会话内容"""
    try:
        results = await api.search_conversations(query_terms=query_terms, limit=limit, search_scope=search_scope)
        
        response = f"🔍 Search Results (Scope: {search_scope})\n\n"
        response += f"📊 Found {len(results)} conversations\n\n"
        
        for i, result in enumerate(results[:5], 1):  # Show top 5 results
            response += f"{i}. "
            if 'summary' in result:
                response += f"{result['summary'][:100]}...\n"
            elif 'content' in result:
                response += f"{result['content'][:100]}...\n"
            
            if 'technical_terms' in result and result['technical_terms']:
                response += f"   🔧 Tech terms: {', '.join(result['technical_terms'][:3])}\n"
            
            if 'compression_ratio' in result and result['compression_ratio'] < 1.0:
                savings = int((1 - result['compression_ratio']) * 100)
                response += f"   💾 Compression: {savings}% savings\n"
            
            response += "\n"
        
        if len(results) > 5:
            response += f"... and {len(results) - 5} more results\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        return f"❌ Failed to search conversations: {str(e)}"

async def save_message_tool(role: str, content: str, topics: Optional[List[str]] = None, keywords: Optional[List[str]] = None) -> str:
    """保存消息到系统"""
    try:
        result = await api.save_message(role=role, content=content, topics=topics or [], keywords=keywords or [])
        
        message_id = result.get("message_id", "")
        compression_ratio = result.get("compression_ratio", 1.0)
        content_length = result.get("content_length", len(content))
        tech_terms_count = result.get("technical_terms_extracted", 0)
        
        response = f"✅ Message saved successfully!\n\n"
        response += f"🆔 Message ID: {message_id}\n"
        response += f"📏 Content Length: {content_length} characters\n"
        
        if compression_ratio < 1.0:
            savings = int((1 - compression_ratio) * 100)
            response += f"💾 Compression: {compression_ratio:.2f} ratio ({savings}% savings)\n"
        
        if tech_terms_count > 0:
            response += f"🔧 Technical terms extracted: {tech_terms_count}\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        return f"❌ Failed to save message: {str(e)}"

async def analyze_compression_tool(text: str) -> str:
    """分析文本的压缩潜力"""
    try:
        analysis = await api.analyze_compression(text)
        
        original_length = analysis.get('original_length', len(text))
        compression_ratio = analysis.get('compression_ratio', 1.0)
        bytes_saved = analysis.get('bytes_saved', 0)
        short_summary = analysis.get('short_summary', '')
        tech_terms = analysis.get('technical_terms', [])
        
        response = f"🔬 Compression Analysis Results\n\n"
        response += f"📏 Original Length: {original_length} characters\n"
        
        if compression_ratio < 1.0:
            savings_pct = int((1 - compression_ratio) * 100)
            response += f"�� Compression Ratio: {compression_ratio:.2f} ({savings_pct}% savings)\n"
            response += f"📉 Bytes Saved: {bytes_saved:,}\n"
        
        if short_summary:
            response += f"\n📋 Generated Summary:\n{short_summary}\n"
        
        if tech_terms:
            response += f"\n🔧 Technical Terms Found ({len(tech_terms)}):\n"
            response += f"   {', '.join(tech_terms[:8])}\n"
            if len(tech_terms) > 8:
                response += f"   ... and {len(tech_terms) - 8} more\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing compression: {e}")
        return f"❌ Failed to analyze compression: {str(e)}"

async def save_insight_tool(insight_type: str, content: str, summary: str = "", 
                           source_messages: Optional[List[str]] = None, relevance_score: float = 0.8,
                           business_area: str = "", impact_level: str = "medium",
                           actionable_items: Optional[List[str]] = None) -> str:
    """保存洞察到系统"""
    try:
        insight_id = await api.save_insight(
            insight_type=insight_type,
            content=content,
            summary=summary,
            source_messages=source_messages or [],
            relevance_score=relevance_score,
            business_area=business_area,
            impact_level=impact_level,
            actionable_items=actionable_items or []
        )
        
        response = f"✅ Insight saved successfully!\n\n"
        response += f"🆔 Insight ID: {insight_id}\n"
        response += f"📊 Type: {insight_type}\n"
        response += f"⭐ Relevance Score: {relevance_score:.1f}\n"
        response += f"🏢 Business Area: {business_area}\n"
        response += f"📈 Impact Level: {impact_level}\n"
        
        if actionable_items:
            response += f"\n🎯 Actionable Items ({len(actionable_items)}):\n"
            for item in actionable_items[:3]:
                response += f"  • {item}\n"
            if len(actionable_items) > 3:
                response += f"  ... and {len(actionable_items) - 3} more items\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error saving insight: {e}")
        return f"❌ Failed to save insight: {str(e)}"

# === MCP TOOL REGISTRY ===

MCP_TOOLS = {
    "record_current_conversation_tool": {
        "function": record_current_conversation,
        "description": "Record the current conversation exchange with smart compression and adaptive context",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_message": {"type": "string", "description": "The user's message"},
                "assistant_message": {"type": "string", "description": "The assistant's response message"},
                "topics": {"type": "array", "items": {"type": "string"}, "description": "Related topics (optional)"},
                "keywords": {"type": "array", "items": {"type": "string"}, "description": "Key terms (optional)"}
            },
            "required": ["user_message", "assistant_message"]
        }
    },
    "get_analytics_tool": {
        "function": get_analytics_tool,
        "description": "Get system analytics including message counts, compression statistics, and technical term analysis",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_context_tool": {
        "function": get_context_tool,
        "description": "Retrieve adaptive context information with configurable detail levels",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of context items to retrieve", "default": 5},
                "detail_level": {"type": "string", "enum": ["short", "medium", "full", "adaptive"], "description": "Level of detail for context", "default": "medium"},
                "format_type": {"type": "string", "enum": ["narrative", "bullet", "structured"], "description": "Format type for context", "default": "narrative"}
            },
            "required": []
        }
    },
    "search_conversations_tool": {
        "function": search_conversations_tool,
        "description": "Search conversations with enhanced scope options and technical term matching",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query_terms": {"type": "array", "items": {"type": "string"}, "description": "Search terms to find"},
                "limit": {"type": "integer", "description": "Maximum number of results", "default": 10},
                "search_scope": {"type": "string", "enum": ["all", "technical", "topics", "summaries"], "description": "Search scope", "default": "all"}
            },
            "required": ["query_terms"]
        }
    },
    "save_message_tool": {
        "function": save_message_tool,
        "description": "Save a message to the system with compression and technical term extraction",
        "inputSchema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "enum": ["user", "assistant", "system"], "description": "Message role"},
                "content": {"type": "string", "description": "Message content"},
                "topics": {"type": "array", "items": {"type": "string"}, "description": "Related topics (optional)"},
                "keywords": {"type": "array", "items": {"type": "string"}, "description": "Key terms (optional)"}
            },
            "required": ["role", "content"]
        }
    },
    "analyze_compression_tool": {
        "function": analyze_compression_tool,
        "description": "Analyze text compression potential with summary generation and technical term extraction",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze for compression potential"}
            },
            "required": ["text"]
        }
    },
    "save_insight_tool": {
        "function": save_insight_tool,
        "description": "Save insights with business impact analysis and actionable items",
        "inputSchema": {
            "type": "object",
            "properties": {
                "insight_type": {"type": "string", "enum": ["solution", "problem", "trend", "opportunity"], "description": "Type of insight"},
                "content": {"type": "string", "description": "Insight content"},
                "summary": {"type": "string", "description": "Brief summary of the insight", "default": ""},
                "source_messages": {"type": "array", "items": {"type": "string"}, "description": "Source message IDs (optional)"},
                "relevance_score": {"type": "number", "minimum": 0, "maximum": 1, "description": "Relevance score (0-1)", "default": 0.8},
                "business_area": {"type": "string", "description": "Business area or domain", "default": ""},
                "impact_level": {"type": "string", "enum": ["low", "medium", "high", "critical"], "description": "Impact level", "default": "medium"},
                "actionable_items": {"type": "array", "items": {"type": "string"}, "description": "List of actionable items (optional)"}
            },
            "required": ["insight_type", "content"]
        }
    }
}

# === MCP MESSAGE HANDLER ===

class MCPMessageHandler:
    """处理MCP协议消息"""
    
    def __init__(self):
        self.initialized = False
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP消息并返回响应"""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        logger.info(f"Processing MCP method: {method}")
        
        try:
            if method == "initialize":
                return await self._handle_initialize(msg_id, params)
            elif method == "notifications/initialized":
                return await self._handle_initialized_notification(msg_id, params)
            elif method == "tools/list":
                return await self._handle_tools_list(msg_id)
            elif method == "tools/call":
                return await self._handle_tools_call(msg_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling MCP message: {e}")
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, msg_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        self.initialized = True
        logger.info(f"MCP Server initialized with params: {params}")
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "prompts": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False}
                },
                "serverInfo": {
                    "name": "Enhanced Conversation System MCP Server",
                    "version": "2.0.0"
                }
            }
        }
    
    async def _handle_initialized_notification(self, msg_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化完成通知"""
        logger.info(f"Client initialization completed with params: {params}")
        
        # For notifications, we don't need to return a response with an id
        # But we'll return a success response anyway for compatibility
        return {
            "jsonrpc": "2.0",
            "result": "ok"
        }
    
    async def _handle_tools_list(self, msg_id: Any) -> Dict[str, Any]:
        """处理工具列表请求"""
        tools = []
        for tool_name, tool_config in MCP_TOOLS.items():
            tools.append({
                "name": tool_name,
                "description": tool_config["description"],
                "inputSchema": tool_config["inputSchema"]
            })
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": tools}
        }
    
    async def _handle_tools_call(self, msg_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in MCP_TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        tool_config = MCP_TOOLS[tool_name]
        tool_function = tool_config["function"]
        
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        try:
            result = await tool_function(**arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }

# Global message handler
message_handler = MCPMessageHandler()

# === FASTAPI APP WITH SSE ===

app = FastAPI(title="Enhanced Conversation System MCP Server", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SSE ENDPOINT ===

@app.get("/sse")
@app.post("/sse")
@app.options("/sse")
async def sse_endpoint(request: Request):
    """SSE端点 - MCP over Server-Sent Events，支持GET、POST和OPTIONS"""
    
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            }
        )
    
    # For Cursor and other MCP clients, we need to handle both GET and POST
    if request.method == "POST":
        # Handle POST request for immediate message processing
        try:
            body = await request.json()
            logger.info(f"SSE POST request with body: {body}")
            
            # Process the message immediately for POST requests
            response = await message_handler.handle_message(body)
            return JSONResponse(content=response)
            
        except Exception as e:
            logger.error(f"Error processing SSE POST: {e}")
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": f"Invalid request: {str(e)}"
                }
            }, status_code=400)
    
    # Handle GET request for SSE stream
    async def event_stream():
        logger.info("SSE connection established")
        
        try:
            # Send initial connection confirmation
            yield f"event: connected\n"
            yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Keep connection alive with periodic pings
            while True:
                await asyncio.sleep(30)
                # Send keepalive ping
                yield f"event: ping\n"
                yield f"data: {json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})}\n\n"
                
        except asyncio.CancelledError:
            logger.info("SSE connection closed")
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
        }
    )

# === MESSAGE ENDPOINT ===

class MCPMessage(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None

@app.post("/message")
async def message_endpoint(message: MCPMessage):
    """Message端点 - 处理MCP请求并通过SSE返回响应"""
    
    logger.info(f"Received MCP message: {message.method}")
    
    # Process the message
    response = await message_handler.handle_message(message.dict())
    
    # Return the response directly (for SSE clients, this gets sent over the SSE connection)
    return JSONResponse(content=response)

# === HEALTH CHECK ===

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check API connection
        api_health = await api.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "mcp_server": "v2.0.0",
            "transport": "sse",
            "api_backend": api_health,
            "initialized": message_handler.initialized
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# === ROOT ENDPOINT FOR COMPATIBILITY ===

@app.get("/")
async def root():
    """Root endpoint with MCP server information"""
    return {
        "name": "Enhanced Conversation System MCP Server",
        "version": "2.0.0",
        "transport": "sse",
        "endpoints": {
            "sse": "/sse",
            "message": "/message",
            "health": "/health"
        },
        "description": "MCP Server with SSE transport for enhanced conversation management"
    }

if __name__ == "__main__":
    # Configure server parameters
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "3001"))
    
    logger.info(f"🚀 Starting Enhanced MCP Server v2.0 with SSE Transport...")
    logger.info(f"🌐 Server will listen on {host}:{port}")
    logger.info(f"🔗 API Backend: {api.base_url}")
    logger.info(f"📡 SSE Endpoint: http://{host}:{port}/sse")
    logger.info(f"💬 Message Endpoint: http://{host}:{port}/message")
    
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
