from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional

# Base response models
class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    detail: str
    status_code: int

# Farmer response models
class FarmerResponse(BaseModel):
    """Response for farmer creation, update, and get operations"""
    farmer_id: str
    name: str
    mobile_no: str
    language: str
    created_at: datetime
    state: Optional[str] = None
    district: Optional[str] = None

# Farm response models
class FarmResponse(BaseModel):
    """Response for farm operations"""
    farm_id: str
    farmer_id: str
    farm_name: str
    size: float
    state: str
    district: str
    created_at: datetime

# Crop response models
class CropResponse(BaseModel):
    """Response for crop creation"""
    crop_id: str
    farm_id: str
    crop_name: str
    crop_variety: str
    description: str
    previous_crop: str
    previous_crop_yield: str
    planted_at: Optional[datetime] = None

class CropsListResponse(BaseModel):
    """Response for getting list of crops"""
    crops: List[CropResponse]
    count: int

# Post response models
class PostResponse(BaseModel):
    """Response for post creation and individual post data"""
    id: str
    user_id: str
    content_url: str
    content_desc: str
    likes: int
    reports: int
    created_at: datetime
    comment_ids: List[str] = []

class PostDeleteResponse(BaseResponse):
    """Response for post deletion"""
    message: str = "Post deleted successfully"

class PostFeedResponse(BaseModel):
    """Response for posts feed"""
    posts: List[PostResponse]
    count: int

class PostActionResponse(BaseResponse):
    """Response for like/dislike actions"""
    message: str

# Comment response models
class CommentResponse(BaseModel):
    """Response for comment creation and individual comment data"""
    id: str
    user_id: str
    content: str
    post_id: str
    created_at: datetime

class CommentDeleteResponse(BaseResponse):
    """Response for comment deletion"""
    message: str = "Comment deleted successfully"

class CommentsListResponse(BaseModel):
    """Response for getting comments for a post"""
    comments: List[CommentResponse]
    count: int

# Chat response models
class ChatMessageResponse(BaseModel):
    """Response for chat message"""
    response: str
    user_id: str

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatHistoryResponse(BaseModel):
    """Response for chat history"""
    user_id: str
    messages: List[ChatMessage]
    count: int

class ChatClearResponse(BaseResponse):
    """Response for clearing chat history"""
    user_id: str
    message: str = "Chat history cleared successfully"

# Market data response models
class MarketRecord(BaseModel):
    """Individual market record"""
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
    arrival_date: str
    min_price: float
    max_price: float
    modal_price: float

class MarketDataResponse(BaseModel):
    """Response for market data"""
    status: str
    records: List[Dict[str, Any]]
    count: int
    message: str

# Weather response models
class WeatherLocation(BaseModel):
    """Weather location data"""
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str

class WeatherCurrent(BaseModel):
    """Current weather data"""
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: str
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    vis_km: float
    vis_miles: float
    uv: float
    gust_mph: float
    gust_kph: float

class WeatherDayData(BaseModel):
    """Essential day weather data"""
    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    avgtemp_c: float
    avgtemp_f: float
    condition: str
    totalprecip_mm: float
    totalprecip_in: float
    maxwind_mph: float
    maxwind_kph: float
    avghumidity: int
    uv: float

class WeatherAstroData(BaseModel):
    """Essential astronomical data"""
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str

class WeatherForecastDay(BaseModel):
    """Simplified weather forecast for a day"""
    date: str
    day: WeatherDayData
    astro: WeatherAstroData

class WeatherForecast(BaseModel):
    """Weather forecast data"""
    forecast: List[WeatherForecastDay]

class WeatherData(BaseModel):
    """Individual weather data for a location"""
    location: WeatherLocation
    current: WeatherCurrent
    forecast: WeatherForecast

class WeatherResponse(BaseModel):
    """Response for weather data - flexible to handle farm-keyed data"""
    model_config = {
        "extra": "allow"
    }

# Image detection response models
class ImageDetectionResponse(BaseModel):
    """Response for image detection"""
    analysis: str
    language: str
    user_id: str
