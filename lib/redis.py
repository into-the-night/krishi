import redis
import json
from typing import List, Dict, Optional
from datetime import datetime

class Redis:
    def __init__(self):
        self.client = redis.Redis(
            host="localhost", 
            port=6379, 
            db=0,
            decode_responses=True  # Automatically decode responses to strings
        )

    def add_message(self, user_id: str, message: Dict) -> None:
        """Add a message to user's chat history"""
        now = datetime.utcnow().isoformat()
        # Get existing history
        history = self.get_chat_history(user_id)
        
        if isinstance(message, list):
            for msg in message:
                if 'timestamp' not in msg:
                    msg['timestamp'] = now
            history.extend(message)
        else:
            if 'timestamp' not in message:
                message['timestamp'] = now
            history.append(message)
        
        # Store back to Redis
        self.client.set(f"chat:{user_id}", json.dumps(history))
    
    def get_chat_history(self, user_id: str) -> List[Dict]:
        """Get full chat history for a user"""
        history_str = self.client.get(f"chat:{user_id}")
        if history_str:
            return json.loads(history_str)
        return []
    
    def get_recent_messages(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from chat history"""
        history = self.get_chat_history(user_id)
        return history[-limit:] if history else []
    
    def clear_chat_history(self, user_id: str) -> None:
        """Clear chat history for a user"""
        self.client.delete(f"chat:{user_id}")
    
    def update_last_message(self, user_id: str, update_data: Dict) -> None:
        """Update the last message (useful for adding tool calls or other metadata)"""
        history = self.get_chat_history(user_id)
        if history:
            history[-1].update(update_data)
            self.client.set(f"chat:{user_id}", json.dumps(history))
