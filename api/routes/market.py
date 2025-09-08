from fastapi import APIRouter
from api.models.requests import MarketDataRequest
import requests
from config.settings import settings

router = APIRouter(prefix="/market", tags=["market"])

@router.post("/get")
def get_market_data(request: MarketDataRequest):
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": settings.ogd_api_key,
        "format": "json",
        "limit": request.limit,
        "state": request.state,
        "district": request.district,
        "market": request.market,
        "commodity": request.commodity,
        "variety": request.variety,
        "grade": request.grade,
        "offset": request.offset,
    }
    response = requests.get(base_url, params=params)
    return response.json()