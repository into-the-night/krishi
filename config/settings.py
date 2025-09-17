from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

class Settings(BaseSettings):
    ogd_api_key: str = Field(...)
    roboflow_api_key: str = Field(...)
    gemini_api_key: str = Field(...)
    tavily_api_key: str = Field(...)
    weather_api_key: str = Field(...)
    redis_url: str = Field("localhost:6379")
    supabase_uri: str = Field(...)
    supabase_key: str = Field(...)
    supabase_service_key: str = Field(...)
    firebase_credentials_path: str = Field("firebase-creds.json")
    celery_broker_url: str = Field("redis://localhost:6379/0")
    deepgram_api_key: str = Field(...)

settings = Settings()