from fastapi import APIRouter, HTTPException, Depends
import httpx
from lib.db import get_farms, get_supabase
from supabase import AsyncClient

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/get")
async def get_weather(farmer_id: str, supabase: AsyncClient = Depends(get_supabase)):
    """Get weather data for a user"""
    farms = await get_farms(farmer_id)
    if not farms:
        raise HTTPException(status_code=404, detail="Farms not found")
    weather_data = {}

    for farm in farms:
        weather_url = f"http://api.weatherapi.com/v1/forecast.json?q={farm.district},{farm.state}"
        async with httpx.AsyncClient() as client:
            response = await client.get(weather_url)
            if response.status_code != 200 or not response.json():
                raise HTTPException(status_code=400, detail="Failed to get weather data")
            weather_data = response.json()
            weather_data.update({farm.farm_name: weather_data})

    return weather_data