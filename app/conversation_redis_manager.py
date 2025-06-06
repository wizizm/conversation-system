#!/usr/bin/env python3
"""
会話履歴Redis保存・検索システム
Production-ready implementation for conversation knowledge accumulation
"""

import datetime
import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List
from uuid import uuid4

import redis
from dotenv import load_dotenv

# load .env with explicit path
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """会話メッセージの構造化データ"""
    id: str
    timestamp: str
    role: str  # 'user' or 'assistant'
    content: str
    topics: List[str]
    keywords: List[str]
    context_hash: str
    session_id: str

@dataclass
class ConversationInsight:
    """会話から抽出された知見"""
    id: str
    timestamp: str
    insight_type: str  # 'pattern', 'solution', 'framework', 'blind_spot'
    content: str
    source_messages: List[str]
    relevance_score: float
    business_area: str

class ConversationRedisManager:
    """Redis-based conversation management system"""
    
    def __init__(self, host='localhost', port=6379, db=0, password=None, 
                 use_ssl=False, decode_responses=True):
        """Initialize Redis connection with Upstash support"""
        try:
            self.redis_client = redis.Redis(
                host=host, 
                port=port, 
                db=db,
                password=password,
                ssl=use_ssl,
                decode_responses=decode_responses,
                socket_connect_timeout=10,
                socket_timeout=10,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # 接続テスト
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def save_message(self, role: str, content: str, topics: List[str] = None, 
                    keywords: List[str] = None, session_id: str = None) -> str:
        """
        Save a conversation message to Redis
        Returns message ID for reference
        """
        message_id = str(uuid4())
        timestamp = datetime.datetime.now().isoformat()
        timestamp_numeric = datetime.datetime.now().timestamp()
        context_hash = hashlib.md5(content.encode()).hexdigest()
        
        if session_id is None:
            session_id = self._get_or_create_session()
        
        message = ConversationMessage(
            id=message_id,
            timestamp=timestamp,
            role=role,
            content=content,
            topics=topics or [],
            keywords=keywords or [],
            context_hash=context_hash,
            session_id=session_id
        )
        
        # Store message in multiple Redis structures for efficient querying
        pipe = self.redis_client.pipeline()
        
        # 1. Store full message data (convert lists to JSON strings)
        message_dict = asdict(message)
        message_dict['topics'] = json.dumps(message_dict['topics'])
        message_dict['keywords'] = json.dumps(message_dict['keywords'])
        pipe.hset(f"message:{message_id}", mapping=message_dict)
        
        # 2. Add to chronological index
        pipe.zadd("messages:timeline", {message_id: timestamp_numeric})
        
        # 3. Add to session index
        pipe.sadd(f"session:{session_id}:messages", message_id)
        
        # 4. Index by topics
        for topic in (topics or []):
            pipe.sadd(f"topic:{topic.lower()}", message_id)
        
        # 5. Index by keywords
        for keyword in (keywords or []):
            pipe.sadd(f"keyword:{keyword.lower()}", message_id)
        
        # 6. Store role-based index
        pipe.sadd(f"role:{role}", message_id)
        
        pipe.execute()
        
        logger.info(f"Saved message {message_id} to Redis")
        return message_id
    
    def save_insight(self, insight_type: str, content: str, source_messages: List[str],
                    relevance_score: float, business_area: str) -> str:
        """Save extracted insight to Redis"""
        insight_id = str(uuid4())
        timestamp = datetime.datetime.now().isoformat()
        timestamp_numeric = datetime.datetime.now().timestamp()
        
        insight = ConversationInsight(
            id=insight_id,
            timestamp=timestamp,
            insight_type=insight_type,
            content=content,
            source_messages=source_messages,
            relevance_score=relevance_score,
            business_area=business_area
        )
        
        pipe = self.redis_client.pipeline()
        
        # Store insight data (convert lists to JSON strings)
        insight_dict = asdict(insight)
        insight_dict['source_messages'] = json.dumps(insight_dict['source_messages'])
        pipe.hset(f"insight:{insight_id}", mapping=insight_dict)
        
        # Index by type
        pipe.sadd(f"insights:{insight_type}", insight_id)
        
        # Index by business area
        pipe.sadd(f"business_area:{business_area}", insight_id)
        
        # Relevance-based ranking
        pipe.zadd("insights:by_relevance", {insight_id: relevance_score})
        
        pipe.execute()
        
        logger.info(f"Saved insight {insight_id} to Redis")
        return insight_id
    
    def get_conversation_context(self, limit: int = 50) -> Dict[str, Any]:
        """
        Retrieve recent conversation context for feeding to AI
        Returns structured data optimized for AI consumption
        """
        # Get recent messages
        recent_message_ids = self.redis_client.zrevrange("messages:timeline", 0, limit-1)
        
        messages = []
        topics_frequency = {}
        keywords_frequency = {}
        
        for msg_id in recent_message_ids:
            msg_data = self.redis_client.hgetall(f"message:{msg_id}")
            if msg_data:
                messages.append({
                    'role': msg_data['role'],
                    'content': msg_data['content'][:500],  # Truncate for context
                    'timestamp': msg_data['timestamp'],
                    'topics': json.loads(msg_data.get('topics', '[]')),
                    'keywords': json.loads(msg_data.get('keywords', '[]'))
                })
                
                # Count topic frequency
                for topic in json.loads(msg_data.get('topics', '[]')):
                    topics_frequency[topic] = topics_frequency.get(topic, 0) + 1
                
                # Count keyword frequency
                for keyword in json.loads(msg_data.get('keywords', '[]')):
                    keywords_frequency[keyword] = keywords_frequency.get(keyword, 0) + 1
        
        # Get top insights
        top_insights = self._get_top_insights(10)
        
        return {
            'recent_messages': messages,
            'frequent_topics': sorted(topics_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            'frequent_keywords': sorted(keywords_frequency.items(), key=lambda x: x[1], reverse=True)[:15],
            'key_insights': top_insights,
            'total_messages': self.redis_client.zcard("messages:timeline"),
            'context_generated_at': datetime.datetime.now().isoformat()
        }
    
    def search_conversations(self, query_terms: List[str], limit: int = 20) -> List[Dict]:
        """Search conversations by topics or keywords"""
        matching_message_ids = set()
        
        for term in query_terms:
            # Search in topics
            topic_matches = self.redis_client.smembers(f"topic:{term.lower()}")
            matching_message_ids.update(topic_matches)
            
            # Search in keywords
            keyword_matches = self.redis_client.smembers(f"keyword:{term.lower()}")
            matching_message_ids.update(keyword_matches)
        
        # Retrieve and rank results
        results = []
        for msg_id in list(matching_message_ids)[:limit]:
            msg_data = self.redis_client.hgetall(f"message:{msg_id}")
            if msg_data:
                results.append({
                    'id': msg_id,
                    'role': msg_data['role'],
                    'content': msg_data['content'],
                    'timestamp': msg_data['timestamp']
                })
        
        # Sort by timestamp (most recent first)
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        return results
    
    def _get_or_create_session(self) -> str:
        """Get current session or create new one"""
        today = datetime.date.today().isoformat()
        session_key = f"session:{today}"
        
        if not self.redis_client.exists(session_key):
            session_id = str(uuid4())
            self.redis_client.setex(session_key, 86400, session_id)  # 24 hour expiry
            return session_id
        
        return self.redis_client.get(session_key)
    
    def _get_top_insights(self, limit: int) -> List[Dict]:
        """Get top insights by relevance score"""
        top_insight_ids = self.redis_client.zrevrange("insights:by_relevance", 0, limit-1)
        
        insights = []
        for insight_id in top_insight_ids:
            insight_data = self.redis_client.hgetall(f"insight:{insight_id}")
            if insight_data:
                insights.append({
                    'type': insight_data['insight_type'],
                    'content': insight_data['content'],
                    'business_area': insight_data['business_area'],
                    'relevance_score': float(insight_data['relevance_score']),
                    'source_messages': json.loads(insight_data.get('source_messages', '[]'))
                })
        
        return insights
    
    def export_for_ai_context(self, format_type: str = "structured") -> str:
        """
        Export conversation context in format optimized for AI consumption
        """
        context = self.get_conversation_context()
        
        if format_type == "structured":
            return json.dumps(context, indent=2, ensure_ascii=False)
        
        elif format_type == "narrative":
            # Create narrative summary for AI
            narrative_parts = []
            
            narrative_parts.append("## 会話履歴の要約")
            narrative_parts.append(f"総メッセージ数: {context['total_messages']}")
            
            if context['frequent_topics']:
                narrative_parts.append("\n### 頻出トピック:")
                for topic, count in context['frequent_topics'][:5]:
                    narrative_parts.append(f"- {topic} ({count}回)")
            
            if context['key_insights']:
                narrative_parts.append("\n### 重要な知見:")
                for insight in context['key_insights'][:3]:
                    narrative_parts.append(f"- [{insight['type']}] {insight['content'][:200]}...")
            
            narrative_parts.append(f"\n### 最近の会話傾向:")
            recent_user_msgs = [m for m in context['recent_messages'][-10:] if m['role'] == 'user']
            if recent_user_msgs:
                narrative_parts.append("ユーザーは以下の領域に関心を示している:")
                for msg in recent_user_msgs[-3:]:
                    narrative_parts.append(f"- {msg['content'][:150]}...")
            
            return "\n".join(narrative_parts)
        
        return json.dumps(context, ensure_ascii=False)

# Usage example and CLI interface
def main():
    """Example usage demonstrating the system"""
    manager = ConversationRedisManager()
    
    # Example: Save a conversation
    user_msg_id = manager.save_message(
        role="user",
        content="あなたとの会話をローカルで動作するRedisに保存する方法はあるでしょうか？",
        topics=["Redis", "会話履歴", "データ保存"],
        keywords=["Redis", "ローカル", "保存", "会話"]
    )
    
    assistant_msg_id = manager.save_message(
        role="assistant", 
        content="あなたの会話履歴をRedisに保存し、知見を蓄積するシステムは確実に構築可能です。",
        topics=["Redis", "システム設計", "データアーキテクチャ"],
        keywords=["Redis", "システム", "設計", "実装"]
    )
    
    # Save an insight
    manager.save_insight(
        insight_type="solution",
        content="Redis-based conversation storage enables knowledge accumulation and context-aware AI responses",
        source_messages=[user_msg_id, assistant_msg_id],
        relevance_score=0.9,
        business_area="AI/データ管理"
    )
    
    # Get context for AI
    context = manager.export_for_ai_context("narrative")
    print("AI用コンテキスト:")
    print(context)

if __name__ == "__main__":
    main()