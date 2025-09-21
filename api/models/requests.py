from pydantic import BaseModel
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
    language: str = "en"
    
class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    user_id: str

class TTSRequest(BaseModel):
    user_id: str
    message_id: str
    message: str
    language: str = "en"

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

class CreatePostRequest(BaseModel):
    user_id: str
    content_url: str
    content_desc: str

class LikeDislikePostRequest(BaseModel):
    post_id: str

class CreateCommentRequest(BaseModel):
    post_id: str
    user_id: str
    content: str

class DeleteCommentRequest(BaseModel):
    comment_id: str
    user_id: str