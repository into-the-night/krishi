from fastapi import APIRouter, HTTPException

from lib.db import create_farmer, get_farmer, update_farmer
from api.models.requests import CreateFarmerRequest, UpdateFarmerRequest
from api.models.responses import FarmerResponse

router = APIRouter(prefix="/farmer", tags=["farmer"])

@router.post("/create", response_model=FarmerResponse)
async def create(farmer: CreateFarmerRequest) -> FarmerResponse:
    farmer = await create_farmer(
        farmer.name,
        farmer.mobile_no,
        farmer.language,
    )
    if not farmer:
        raise HTTPException(status_code=400, detail="Failed to create farmer")
    return farmer

@router.post("/update", response_model=FarmerResponse)
async def update(farmer: UpdateFarmerRequest) -> FarmerResponse:
    farmer = await update_farmer(
        farmer.farmer_id,
        farmer.name,
        farmer.mobile_no,
        farmer.language,
        farmer.state,
        farmer.district,
    )
    if not farmer:
        raise HTTPException(status_code=400, detail="Failed to update farmer")
    return farmer

@router.get("/get/{farmer_id}", response_model=FarmerResponse)
async def get(farmer_id: str) -> FarmerResponse:
    farmer = await get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(status_code=400, detail="Failed to get farmer")
    return farmer