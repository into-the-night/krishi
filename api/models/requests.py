from pydantic import BaseModel
from fastapi import File, UploadFile
from datetime import datetime

class MarketDataRequest(BaseModel):
    limit: int = 10
    state: str = ""
    district: str = ""
    market: str = ""
    commodity: str = ""
    variety: str = ""
    grade: str = ""
    offset: int = 0
    
class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    user_id: str

class ImageDetectionRequest(BaseModel):
    image: UploadFile = File(...)
    language: str = "en"
    user_id: str

class CreateFarmerRequest(BaseModel):
    name: str
    mobile_no: str
    language: str

class UpdateFarmerRequest(BaseModel):
    farmer_id: str
    name: str = ""
    mobile_no: str = ""
    language: str = ""
    state: str = ""
    district: str = ""

class CreateCropRequest(BaseModel):
    farmer_id: str
    crop_name: str
    crop_variety: str
    description: str
    planted_at: datetime
    previous_crop: str
    previous_crop_yield: str
    farm_name: str
    farm_size: float
    state: str
    district: str
    fcm_key: str