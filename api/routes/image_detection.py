from fastapi import APIRouter, File, UploadFile, Form
from inference_sdk import InferenceHTTPClient
from config.settings import settings
from agent.bot import Bot
from lib.redis import Redis
from lib.db import save_to_supabase
from api.models.responses import ImageDetectionResponse
import tempfile
import uuid
import os

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=settings.roboflow_api_key
)


router = APIRouter(prefix="/image_detection", tags=["image_detection"])
bot = Bot()
redis_client = Redis()

@router.post("/detect", response_model=ImageDetectionResponse)
async def image_detection(
    image: UploadFile = File(...),
    language: str = Form("en"),
    user_id: str = Form(...)
) -> ImageDetectionResponse:
    # Read the image content
    image_content = await image.read()
    
    # Create a temporary file with appropriate extension
    file_extension = ""
    if image.filename and "." in image.filename:
        file_extension = f".{image.filename.split('.')[-1]}"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(image_content)
        tmp_file_path = tmp_file.name
    
    try:
        # Run the workflow with the file path
        result = client.run_workflow(
            workspace_name="sih-n7y20",
            workflow_id="plant-and-disease-workflow",
            images={
                "image": tmp_file_path
            },
            use_cache=True # cache workflow definition for 15 minutes
        )

        # Analyse the output
        analysis = bot.analyse_output(result, tmp_file_path, language)

        # Upload image to Supabase using a valid key
        file_id = f"uploads/{user_id}_{uuid.uuid4()}{file_extension}"
        response = save_to_supabase(tmp_file_path, file_id, content_type="image/jpeg")

        if response:
            user_message = {
                "role": "user",
                "content": f"file:{file_id}"
            }
            assistant_message = {
                "role": "assistant",
                "content": analysis
            }
            redis_client.add_message(user_id, [user_message, assistant_message])

        return ImageDetectionResponse(
            analysis=analysis,
            language=language,
            user_id=user_id
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
