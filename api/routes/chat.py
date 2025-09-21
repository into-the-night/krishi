import os
from fastapi import APIRouter, Query, Form, Depends, UploadFile, File

from agent.bot import Bot
from lib.redis import Redis
from api.models.requests import ChatRequest, TTSRequest
from api.models.responses import ( 
    ChatMessageResponse,
    ChatHistoryResponse,
    ChatClearResponse,
    TTSResponse
)
from lib.db import (
    save_to_supabase,
    create_message,
    get_message,
    create_presigned_url
)

router = APIRouter(prefix="/chat", tags=["chat"])

bot = Bot()
redis_client = Redis()

@router.post("/message", response_model=ChatMessageResponse)
async def chat(request: ChatRequest) -> ChatMessageResponse:
    # Add user message to history
    user_message = {
        "role": "user",
        "content": request.message
    }
    redis_client.add_message(request.user_id, user_message)
    history = redis_client.get_recent_messages(request.user_id, limit=10)
    
    response = await bot.chat(history, request.language)
    
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
async def get_chat_history(user_id: str, limit: int = Query(default=None)) -> ChatHistoryResponse:
    """Get chat history for a user"""
    if limit:
        messages = redis_client.get_recent_messages(user_id, limit=limit)
    else:
        messages = redis_client.get_chat_history(user_id)
    # Convert any file: URLs to signed URLs
    for message in messages:
        if message['content'].startswith("file:"):
            file_path = message['content'][5:]
            try:
                response = await create_presigned_url(file_path)
                message['content'] = response
            except:
                message['content'] = "Content failed to load..."
    
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
    result = await bot.voice_chat(audio_bytes, user_id=user_id, language=language)
    return {
        "user_id": user_id,
        "user_query": result["user_query"],
        "bot_reply": result["bot_reply"]
    }


@router.post("/tts", response_model=TTSResponse)
async def tts_message(request: TTSRequest) -> TTSResponse:
    """voice chatting with the bot where the user uploads audio and bot replies with text and audio"""
    # Placeholder name for the audio file
    audio_file = None

    try:
        # TODO: for future use
        # Check if message is already TTS'd
        # message = await get_message(request.message_id, content_type="audio/x-wav")
        # if message:
        #     response = await create_presigned_url(message.content)
        #     return TTSResponse(
        #         audio_url=response
        #     )
        
        # If message is not TTS'd, generate TTS and save to supabase
        audio_file = await bot.text_to_speech(request.message)

        file_path = f"uploads/audio/{request.message_id}_{request.language}.wav"
        await save_to_supabase(audio_file, file_path, content_type="audio/x-wav")

        response = await create_presigned_url(file_path)

        # await create_message(request.user_id, request.message_id, "assistant", file_path, "audio/x-wav")

        return TTSResponse(
            audio_url=response
        )
    finally:
        if audio_file:
            os.remove(audio_file)


@router.delete("/delete/{user_id}", response_model=ChatClearResponse)
def clear_chat_history(user_id: str) -> ChatClearResponse:
    """Clear chat history for a user"""
    redis_client.clear_chat_history(user_id)
    return ChatClearResponse(
        user_id=user_id,
        message="Chat history cleared successfully"
    )