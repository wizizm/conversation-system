#!/usr/bin/env python3
"""
FastAPI-based Conversation Management System
Production-ready API for conversation storage and retrieval
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from conversation_redis_manager import ConversationRedisManager
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# load .env with explicit path
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models
class MessageRequest(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    topics: Optional[List[str]] = Field(default=[], description="Message topics")
    keywords: Optional[List[str]] = Field(default=[], description="Message keywords")
    session_id: Optional[str] = Field(default=None, description="Session ID")

class InsightRequest(BaseModel):
    insight_type: str = Field(..., description="Type of insight")
    content: str = Field(..., description="Insight content")
    source_messages: List[str] = Field(..., description="Source message IDs")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    business_area: str = Field(..., description="Business area")

class SearchRequest(BaseModel):
    query_terms: List[str] = Field(..., description="Search terms")
    limit: int = Field(default=20, ge=1, le=100, description="Result limit")

class ContextRequest(BaseModel):
    limit: int = Field(default=50, ge=1, le=200, description="Message limit")
    format_type: str = Field(default="structured", description="Context format")

# Global Redis manager
redis_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global redis_manager
    # Startup
    try:
        # デバッグ: 環境変数の確認
        logger.info(f"Environment variables loaded from: {env_path}")
        logger.info(f"Environment file exists: {env_path.exists()}")
        
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_db = int(os.getenv('REDIS_DB', 0))
        redis_password = os.getenv('REDIS_PASSWORD')
        redis_ssl = os.getenv('REDIS_SSL', 'false').lower() == 'true'
        
        # デバッグ: 環境変数の値確認
        logger.info(f"REDIS_HOST: {redis_host}")
        logger.info(f"REDIS_PORT: {redis_port}")
        logger.info(f"REDIS_PASSWORD: {'***' if redis_password else 'None'}")
        logger.info(f"REDIS_SSL: {redis_ssl}")
        
        logger.info(f"Connecting to Redis at {redis_host}:{redis_port} (SSL: {redis_ssl})")
        
        redis_manager = ConversationRedisManager(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            use_ssl=redis_ssl
        )
        
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    yield
    
    # Shutdown
    if redis_manager:
        logger.info("Shutting down Redis connection")

# FastAPI app
app = FastAPI(
    title="Conversation Management API",
    description="Production-ready API for conversation storage and knowledge management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if redis_manager:
            redis_manager.redis_client.ping()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")

@app.post("/messages", response_model=Dict[str, str])
async def save_message(
    message: MessageRequest,
    background_tasks: BackgroundTasks
):
    """Save a conversation message"""
    try:
        if not redis_manager:
            raise HTTPException(status_code=503, detail="Redis not available")
        
        message_id = redis_manager.save_message(
            role=message.role,
            content=message.content,
            topics=message.topics,
            keywords=message.keywords,
            session_id=message.session_id
        )
        
        # Background task for analytics
        background_tasks.add_task(update_analytics, message_id, message.content)
        
        return {"message_id": message_id, "status": "saved"}
        
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insights", response_model=Dict[str, str])
async def save_insight(insight: InsightRequest):
    """Save an extracted insight"""
    try:
        if not redis_manager:
            raise HTTPException(status_code=503, detail="Redis not available")
        
        insight_id = redis_manager.save_insight(
            insight_type=insight.insight_type,
            content=insight.content,
            source_messages=insight.source_messages,
            relevance_score=insight.relevance_score,
            business_area=insight.business_area
        )
        
        return {"insight_id": insight_id, "status": "saved"}
        
    except Exception as e:
        logger.error(f"Error saving insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=List[Dict])
async def search_conversations(search: SearchRequest):
    """Search conversations by terms"""
    try:
        if not redis_manager:
            raise HTTPException(status_code=503, detail="Redis not available")
        
        results = redis_manager.search_conversations(
            query_terms=search.query_terms,
            limit=search.limit
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context", response_model=Dict[str, Any])
async def get_context(context_req: ContextRequest):
    """Get conversation context for AI"""
    try:
        if not redis_manager:
            raise HTTPException(status_code=503, detail="Redis not available")
        
        context = redis_manager.get_conversation_context(limit=context_req.limit)
        
        if context_req.format_type == "narrative":
            formatted_context = redis_manager.export_for_ai_context("narrative")
            return {"context": formatted_context, "raw_data": context}
        
        return context
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    """Get conversation analytics"""
    try:
        if not redis_manager:
            raise HTTPException(status_code=503, detail="Redis not available")
            
        total_messages = redis_manager.redis_client.zcard("messages:timeline")
        total_insights = redis_manager.redis_client.zcard("insights:by_relevance")
        
        # Get top topics
        topic_keys = redis_manager.redis_client.keys("topic:*")
        topics = []
        for key in topic_keys[:10]:
            count = redis_manager.redis_client.scard(key)
            topic = key.replace("topic:", "")
            topics.append({"topic": topic, "count": count})
        
        topics.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "total_messages": total_messages,
            "total_insights": total_insights,
            "top_topics": topics[:5],
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/data")
async def clear_data(confirm: str):
    """Clear all conversation data (dangerous!)"""
    if confirm != "I_UNDERSTAND_THIS_WILL_DELETE_ALL_DATA":
        raise HTTPException(
            status_code=400, 
            detail="Must provide exact confirmation string"
        )
    
    try:
        if not redis_manager:
            raise HTTPException(status_code=503, detail="Redis not available")
            
        redis_manager.redis_client.flushdb()
        logger.warning("All conversation data cleared")
        return {"status": "cleared", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
def update_analytics(message_id: str, content: str):
    """Update analytics in background"""
    try:
        if not redis_manager:
            return
            
        # Simple analytics update
        redis_manager.redis_client.incr("analytics:total_messages")
        redis_manager.redis_client.incr(f"analytics:daily:{datetime.now().date()}")
        
        # Word count analytics
        word_count = len(content.split())
        redis_manager.redis_client.lpush("analytics:word_counts", word_count)
        redis_manager.redis_client.ltrim("analytics:word_counts", 0, 999)  # Keep last 1000
        
        logger.info(f"Analytics updated for message {message_id}")
        
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
