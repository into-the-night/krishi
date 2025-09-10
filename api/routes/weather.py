from fastapi import APIRouter, HTTPException, Depends
import httpx
from lib.db import get_farms, get_farmer, get_supabase
from supabase import AsyncClient
from typing import Dict, Any
from config.settings import settings
from agent.bot import Bot

router = APIRouter(prefix="/weather", tags=["weather"])
bot = Bot()

@router.get("/get")
async def get_weather(farmer_id: str, supabase: AsyncClient = Depends(get_supabase)) -> Dict[str, Any]:
    """Get weather data for a user"""
    farmer = await get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    farms = await get_farms(farmer_id)
    if not farms:
        raise HTTPException(status_code=404, detail="Farms not found")
    weather_data = {}

    for farm in farms:
        weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={settings.weather_api_key}&q={farm.district},{farm.state}&days=5"
        async with httpx.AsyncClient() as client:
            response = await client.get(weather_url)
            if response.status_code != 200 or not response.json():
                raise HTTPException(status_code=400, detail="Failed to get weather data")
            farm_weather = response.json()
            farm_weather_data = {
                "district": farm_weather["location"]["name"],
                "state": farm_weather["location"]["region"],
                "country": farm_weather["location"]["country"],
                "current": {
                    "temp_c": farm_weather["current"]["temp_c"],
                    "temp_f": farm_weather["current"]["temp_f"],
                    "is_day": farm_weather["current"]["is_day"],
                    "condition": farm_weather["current"]["condition"]["text"],
                    "feelslike_c": farm_weather["current"]["feelslike_c"],
                    "feelslike_f": farm_weather["current"]["feelslike_f"],
                    "precip_mm": farm_weather["current"]["precip_mm"],
                    "precip_in": farm_weather["current"]["precip_in"],
                    "dewpoint_c": farm_weather["current"]["dewpoint_c"],
                    "dewpoint_f": farm_weather["current"]["dewpoint_f"],
                    "humidity": farm_weather["current"]["humidity"],
                    "cloud": farm_weather["current"]["cloud"],
                    "vis_km": farm_weather["current"]["vis_km"],
                    "vis_miles": farm_weather["current"]["vis_miles"],
                    "uv": farm_weather["current"]["uv"],
                },
                "forecast": [
                    {
                        "date": day["date"],
                        "day": {
                            "maxtemp_c": day["day"]["maxtemp_c"],
                            "maxtemp_f": day["day"]["maxtemp_f"],
                            "mintemp_c": day["day"]["mintemp_c"],
                            "mintemp_f": day["day"]["mintemp_f"],
                            "avgtemp_c": day["day"]["avgtemp_c"],
                            "avgtemp_f": day["day"]["avgtemp_f"],
                            "condition": day["day"]["condition"]["text"],
                            "totalprecip_mm": day["day"]["totalprecip_mm"],
                            "totalprecip_in": day["day"]["totalprecip_in"],
                            "maxwind_mph": day["day"]["maxwind_mph"],
                            "maxwind_kph": day["day"]["maxwind_kph"],
                            "avghumidity": day["day"]["avghumidity"],
                            "daily_will_it_rain": day["day"]["daily_will_it_rain"],
                            "daily_chance_of_rain": day["day"]["daily_chance_of_rain"],
                            "daily_will_it_snow": day["day"]["daily_will_it_snow"],
                            "daily_chance_of_snow": day["day"]["daily_chance_of_snow"],
                            "uv": day["day"]["uv"]
                        },
                        "astro": {
                            "sunrise": day["astro"]["sunrise"],
                            "sunset": day["astro"]["sunset"],
                            "moonrise": day["astro"]["moonrise"],
                            "moonset": day["astro"]["moonset"]
                        }
                    } for day in farm_weather["forecast"]["forecastday"]
                ]
            }
            if farmer.language != "en":
                farm_weather_data = bot.translate_weather_data(farm_weather_data, language=farmer.language)
            
            weather_data[farm.farm_name] = farm_weather_data

    return weather_data