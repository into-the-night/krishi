from fastapi import APIRouter
from inference_sdk import InferenceHTTPClient
from config.settings import settings
from agent.bot import Bot
from api.models.requests import ImageDetectionRequest

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=settings.roboflow_api_key
)


router = APIRouter(prefix="/image_detection", tags=["image_detection"])
bot = Bot()

@router.post("/detect")
def image_detection(request: ImageDetectionRequest):
    result = client.run_workflow(
        workspace_name="sih-n7y20",
        workflow_id="plant-and-disease-workflow",
        images={
            "image": request.image.file
        },
        use_cache=True # cache workflow definition for 15 minutes
    )
    analysis = bot.analyse_output(result["output"], request.image.file, request.language)

    return analysis