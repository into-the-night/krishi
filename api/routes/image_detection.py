from fastapi import APIRouter, File, UploadFile, Form
from inference_sdk import InferenceHTTPClient
from config.settings import settings
from agent.bot import Bot
import tempfile
import os

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=settings.roboflow_api_key
)


router = APIRouter(prefix="/image_detection", tags=["image_detection"])
bot = Bot()

@router.post("/detect")
async def image_detection(
    image: UploadFile = File(...),
    language: str = Form("en"),
    user_id: str = Form(...)
):
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
        
        return analysis
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
