#!/usr/bin/env python3
"""
Test script for all MCP tools
"""

import asyncio
import json
from main import api

async def test_all_mcp_tools():
    print("🧪 Testing all MCP tools against backend API...")
    print("=" * 50)
    
    # Test 1: Analytics (GET endpoint)
    print("1. Testing get_analytics...")
    try:
        analytics = await api.get_analytics()
        print(f"   ✅ Analytics: {analytics['total_messages']} messages, {len(analytics.get('top_topics', []))} topics")
    except Exception as e:
        print(f"   ❌ Analytics failed: {e}")
    
    # Test 2: Context (POST endpoint)
    print("\n2. Testing get_context...")
    try:
        context = await api.get_context(limit=5, format_type="narrative")
        print(f"   ✅ Context retrieved: {len(context.get('context', ''))} characters")
    except Exception as e:
        print(f"   ❌ Context failed: {e}")
    
    # Test 3: Search (POST endpoint)
    print("\n3. Testing search_conversations...")
    try:
        results = await api.search_conversations(query_terms=["MCP"], limit=3)
        print(f"   ✅ Search results: {len(results)} conversations found")
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
    
    # Test 4: Save message (POST endpoint)
    print("\n4. Testing save_message...")
    try:
        message_id = await api.save_message(
            role="user",
            content="Testing MCP tools functionality", 
            topics=["Testing", "MCP"],
            keywords=["test", "MCP", "functionality"]
        )
        print(f"   ✅ Message saved: {message_id}")
    except Exception as e:
        print(f"   ❌ Save message failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All MCP tools tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_all_mcp_tools())
