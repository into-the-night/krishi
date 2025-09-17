from fastapi import APIRouter, Query, Form
from agent.bot import Bot
from lib.redis import Redis
from api.models.requests import ChatRequest
from api.models.responses import ChatMessageResponse, ChatHistoryResponse, ChatClearResponse
from lib.db import get_supabase
from fastapi import UploadFile, File
import io

router = APIRouter(prefix="/chat", tags=["chat"])

bot = Bot()
redis_client = Redis()
supabase = get_supabase()

@router.post("/message", response_model=ChatMessageResponse)
def chat(request: ChatRequest) -> ChatMessageResponse:
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
    
    return ChatMessageResponse(
        response=response,
        user_id=request.user_id
    )

@router.get("/history/{user_id}", response_model=ChatHistoryResponse)
def get_chat_history(user_id: str, limit: int = Query(default=None)) -> ChatHistoryResponse:
    """Get chat history for a user"""
    if limit:
        messages = redis_client.get_recent_messages(user_id, limit=limit)
    else:
        messages = redis_client.get_chat_history(user_id)

    for message in messages:
        if message['content'].startswith("file:"):
            file_path = message['content'][5:]
            try:
                response = (
                    supabase.storage
                    .from_("krishi")
                    .create_signed_url(
                        file_path,
                        360
                    )
                )
                message['content'] = response['signedURL']
            except:
                message['content'] = "Image"
    
    return ChatHistoryResponse(
        user_id=user_id,
        messages=messages,
        count=len(messages)
    )


@router.post("/voice")
async def voice_chat(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    language: str = Form(default="en", examples=["en", "hi"])
):
    """voice chatting with the bot where the user uploads audio and bot replies with text and audio"""
    audio_bytes = await audio.read()
    result = bot.voice_chat(audio_bytes, user_id=user_id, language=language)
    return {
        "user_id": user_id,
        "user_query": result["user_query"],
        "bot_reply": result["bot_reply"],
        "bot_audio_url": result.get("bot_audio_url", None),
        "user_audio_url": result.get("user_audio_url", None)
    }

@router.delete("/delete/{user_id}", response_model=ChatClearResponse)
def clear_chat_history(user_id: str) -> ChatClearResponse:
    """Clear chat history for a user"""
    redis_client.clear_chat_history(user_id)
    return ChatClearResponse(
        user_id=user_id,
        message="Chat history cleared successfully"
    )