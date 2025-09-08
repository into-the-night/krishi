from fastapi import APIRouter, HTTPException
from api.models.requests import CreateCropRequest
from lib.db import create_farm, create_crop, get_crops

router = APIRouter(prefix="/crops", tags=["crops"])

@router.post("/create")
async def create(crop: CreateCropRequest):
    farm = await create_farm(
        crop.farmer_id,
        crop.farm_name,
        crop.farm_size,
        crop.district,
        crop.state,
        crop.fcm_key
    )
    if not farm:
        raise HTTPException(status_code=400, detail="Failed to create farm")

    crop = await create_crop(
        farm.farm_id,
        crop.crop_name,
        crop.crop_variety,
        crop.description,
        crop.planted_at,
        crop.previous_crop,
        crop.previous_crop_yield
    )
    if not crop:
        raise HTTPException(status_code=400, detail="Failed to create crop")

    return crop

@router.get("/get/{farmer_id}")
async def get(farmer_id: str):
    crops = await get_crops(farmer_id)
    if not crops:
        raise HTTPException(status_code=400, detail="Failed to get crops")
    return crops