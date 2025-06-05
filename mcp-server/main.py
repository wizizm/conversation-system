#!/usr/bin/env python3
"""
Complete MCP Server for Conversation System using official MCP Python SDK
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("conversation-system")

class ConversationAPI:
    """Complete API client for conversation system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def save_message(self, role: str, content: str, topics: List[str] = None, keywords: List[str] = None) -> str:
        """Save a conversation message"""
        data = {
            "role": role,
            "content": content,
            "topics": topics or [],
            "keywords": keywords or []
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{self.base_url}/messages", json=data)
            response.raise_for_status()
            result = response.json()
            return result.get("message_id", "")
    
    async def get_context(self, limit: int = 50, format_type: str = "narrative") -> Dict[str, Any]:
        """Get conversation context for AI consumption"""
        data = {
            "limit": limit,
            "format_type": format_type
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{self.base_url}/context", json=data)
            response.raise_for_status()
            return response.json()
    
    async def search_conversations(self, query_terms: List[str], limit: int = 20) -> List[Dict]:
        """Search conversations by terms"""
        data = {
            "query_terms": query_terms,
            "limit": limit
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{self.base_url}/search", json=data)
            response.raise_for_status()
            return response.json()
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get conversation analytics"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/analytics")
            response.raise_for_status()
            return response.json()

# Initialize API client
api = ConversationAPI()

# === MCP TOOLS ===

@mcp.tool()
async def record_current_conversation(
    user_message: str,
    assistant_message: str,
    topics: List[str] = None,
    keywords: List[str] = None
) -> str:
    """
    Record the current conversation exchange automatically.
    Use this when user asks to 'save conversation' or 'record this chat'
    
    Args:
        user_message: The user's message in this conversation
        assistant_message: The assistant's response message  
        topics: Topics discussed in this conversation
        keywords: Key terms from the conversation
    """
    try:
        # Save user message
        user_msg_id = await api.save_message("user", user_message, topics, keywords)
        
        # Save assistant message
        assistant_msg_id = await api.save_message("assistant", assistant_message, topics, keywords)
        
        return f"✅ Conversation recorded successfully!\nUser message ID: {user_msg_id}\nAssistant message ID: {assistant_msg_id}"
        
    except Exception as e:
        logger.error(f"Error recording conversation: {e}")
        return f"❌ Error recording conversation: {str(e)}"

@mcp.tool()
async def save_conversation_message(
    role: str,
    content: str,
    topics: List[str] = None,
    keywords: List[str] = None
) -> str:
    """
    Save a single conversation message (user or assistant) to the conversation system.
    
    Args:
        role: Role of the message sender ("user" or "assistant")
        content: Content of the message
        topics: Optional list of topics related to the message
        keywords: Optional list of keywords for the message
    """
    try:
        if role not in ["user", "assistant"]:
            return f"❌ Invalid role: {role}. Must be 'user' or 'assistant'"
        
        message_id = await api.save_message(role, content, topics, keywords)
        
        return f"✅ Message saved successfully!\nMessage ID: {message_id}\nRole: {role}\nTopics: {', '.join(topics) if topics else 'None'}\nKeywords: {', '.join(keywords) if keywords else 'None'}"
        
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        return f"❌ Error saving message: {str(e)}"

@mcp.tool()
async def get_conversation_context(
    limit: int = 50,
    format_type: str = "narrative"
) -> str:
    """
    Get recent conversation history and context for reference.
    
    Args:
        limit: Number of recent messages to retrieve (default: 50)
        format_type: Format of the context response ("structured" or "narrative", default: "narrative")
    """
    try:
        if format_type not in ["structured", "narrative"]:
            return f"❌ Invalid format_type: {format_type}. Must be 'structured' or 'narrative'"
        
        context_data = await api.get_context(limit=limit, format_type=format_type)
        
        if format_type == "narrative":
            response_text = f"📊 Conversation Context (last {limit} messages):\n\n{context_data.get('context', 'No context available')}"
        else:
            response_text = f"📊 Conversation Context (Structured - last {limit} messages):\n\n{json.dumps(context_data, indent=2, ensure_ascii=False)}"
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        return f"❌ Error getting context: {str(e)}"

@mcp.tool()
async def search_conversation_history(
    query_terms: List[str],
    limit: int = 20
) -> str:
    """
    Search previous conversations by topics or keywords.
    
    Args:
        query_terms: List of terms to search for in conversation history
        limit: Maximum number of results to return (default: 20)
    """
    try:
        if not query_terms:
            return "❌ Please provide at least one search term"
        
        results = await api.search_conversations(query_terms=query_terms, limit=limit)
        
        if not results:
            response_text = f"🔍 No conversations found for terms: {', '.join(query_terms)}"
        else:
            response_text = f"🔍 Found {len(results)} conversations for terms: {', '.join(query_terms)}\n\n"
            for i, result in enumerate(results[:10], 1):  # Show max 10 results
                response_text += f"{i}. [{result['role']}] {result['content'][:150]}...\n"
                response_text += f"   📅 {result['timestamp'].split('T')[0]} {result['timestamp'].split('T')[1][:8]}\n"
                if result.get('topics'):
                    response_text += f"   🏷️ Topics: {', '.join(result['topics'])}\n"
                response_text += "\n"
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        return f"❌ Error searching conversations: {str(e)}"

@mcp.tool()
async def get_conversation_analytics() -> str:
    """
    Get analytics and statistics about conversation patterns.
    """
    try:
        analytics = await api.get_analytics()
        
        response_text = f"📈 Conversation Analytics:\n\n"
        response_text += f"📝 Total Messages: {analytics.get('total_messages', 0)}\n"
        response_text += f"💡 Total Insights: {analytics.get('total_insights', 0)}\n\n"
        
        if analytics.get('top_topics'):
            response_text += "🏷️ Top Topics:\n"
            for i, topic in enumerate(analytics['top_topics'][:10], 1):
                response_text += f"  {i}. {topic['topic']}: {topic['count']} times\n"
            response_text += "\n"
        
        if analytics.get('last_updated'):
            response_text += f"🕒 Last Updated: {analytics['last_updated']}\n"
        
        # Additional statistics if available
        if analytics.get('message_count_by_role'):
            response_text += f"\n📊 Message Distribution:\n"
            for role, count in analytics['message_count_by_role'].items():
                response_text += f"  • {role.title()}: {count} messages\n"
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return f"❌ Error getting analytics: {str(e)}"

if __name__ == "__main__":
    # Set environment variable
    os.environ["CONVERSATION_API_URL"] = "http://localhost:8000"
    
    # Test API connection on startup
    async def test_connection():
        try:
            analytics = await api.get_analytics()
            logger.info("✅ API connection successful")
        except Exception as e:
            logger.warning(f"API connection test failed: {e}")
            logger.info("MCP server will continue, but may not work until API is available")
    
    # Run connection test
    asyncio.run(test_connection())
    
    # Run the server
    mcp.run()
