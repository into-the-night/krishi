from datetime import datetime
from pydantic import BaseModel

class Farmer(BaseModel):
    farmer_id: str
    name: str
    mobile_no: str
    language: str
    created_at: datetime

class Farm(BaseModel):
    farm_id: str
    farmer_id: str
    farm_name: str
    size: float
    state: str
    district: str
    created_at: datetime

class Location(BaseModel):
    id: str
    district: str
    state: str
    firebase_topic: str

class Crop(BaseModel):
    crop_id: str
    farm_id: str
    crop_name: str
    crop_variety: str
    description: str
    planted_at: datetime
    previous_crop: str
    previous_crop_yield: str

class Post(BaseModel):
    id: str
    user_id: str
    content_url: str
    content_desc: str
    likes: int
    reports: int
    created_at: datetime
    comment_ids: list[str] = []

class Comment(BaseModel):
    id: str
    user_id: str
    content: str
    likes: int
    created_at: datetime

class Message(BaseModel):
    id: str
    user_id: str
    message_id: str
    role: str
    content: str
    content_type: str
    created_at: datetime