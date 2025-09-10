from fastapi import APIRouter, Query
from agent.bot import Bot
from lib.redis import Redis
from api.models.requests import ChatRequest
from typing import Dict, List
from fastapi import UploadFile, File
import io

router = APIRouter(prefix="/chat", tags=["chat"])

bot = Bot()
redis_client = Redis()

@router.post("/message")
def chat(request: ChatRequest) -> Dict:
    # Add user message to history
    user_message = {
        "role": "user",
        "content": request.message
    }
    redis_client.add_message(request.user_id, user_message)
    history = redis_client.get_recent_messages(request.user_id, limit=10)
    
    response = bot.chat(history, request.language)
    
    # Add assistant response to history
    assistant_message = {
        "role": "assistant",
        "content": response
    }
    redis_client.add_message(request.user_id, assistant_message)
    
    return {
        "response": response,
        "user_id": request.user_id
    }

@router.get("/history/{user_id}")
def get_chat_history(user_id: str, limit: int = Query(default=None)) -> Dict:
    """Get chat history for a user"""
    if limit:
        messages = redis_client.get_recent_messages(user_id, limit=limit)
    else:
        messages = redis_client.get_chat_history(user_id)
    
    return {
        "user_id": user_id,
        "messages": messages,
        "count": len(messages)
    }

@router.post("/voice")
async def voice_chat(user_id: str, language: str | None, audio: UploadFile = File(...)):
    """voice chatting with the bot where the user uploads audio and bot replies with text and audio"""
    audio_bytes = await audio.read()
    result = bot.voice_chat(audio_bytes, user_id=user_id, mimetype=audio.content_type, language=language)
    return {
        "user_id": user_id,
        "user_query": result["user_query"],
        "bot_reply": result["bot_reply"],
        "bot_audio_url": result["bot_audio_url"],
        "user_audio_url": result["user_audio_url"]
    }

@router.delete("/delete/{user_id}")
def clear_chat_history(user_id: str) -> Dict:
    """Clear chat history for a user"""
    redis_client.clear_chat_history(user_id)
    return {
        "user_id": user_id,
        "message": "Chat history cleared successfully"
    }