import requests
from fastapi import APIRouter

from agent.bot import Bot
from config.settings import settings
from api.models.requests import MarketDataRequest
from api.models.responses import MarketDataResponse

router = APIRouter(prefix="/market", tags=["market"])
bot = Bot()

@router.post("/get")
async def get_market_data(request: MarketDataRequest):
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": settings.ogd_api_key,
        "format": "json",
    }
    
    # Add optional parameters
    if request.limit:
        params["limit"] = request.limit
    if request.offset:
        params["offset"] = request.offset
    
    # Add filters with correct format
    if request.state:
        params["filters[state.keyword]"] = request.state
    if request.district:
        params["filters[district]"] = request.district
    if request.market:
        params["filters[market]"] = request.market
    if request.commodity:
        params["filters[commodity]"] = request.commodity
    if request.variety:
        params["filters[variety]"] = request.variety
    if request.grade:
        params["filters[grade]"] = request.grade
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        
        data = response.json()
        records = data.get("records", [])
        
        # Translate if needed
        if request.language != "en":
            records = await bot.translate_market_data(records, request.language)
        
        return MarketDataResponse(
            status="success",
            records=records,
            count=len(records),
            message=f"Found {len(records)} market records"
        )
    except requests.RequestException as e:
        return MarketDataResponse(
            status="error",
            records=[],
            count=0,
            message=f"Error fetching market data: {str(e)}"
        )
    except Exception as e:
        return MarketDataResponse(
            status="error", 
            records=[],
            count=0,
            message=f"An error occurred: {str(e)}"
        )
