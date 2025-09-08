from supabase import create_client
from config.settings import settings
from lib.models import Location, Farmer, Crop, Farm
from lib.firebase import subscribe_to_topic
from datetime import datetime
from uuid import uuid4

supabase = create_client(settings.supabase_uri, settings.supabase_key)

def get_supabase():
    return supabase

async def create_farmer(
    name: str,
    mobile_no: str,
    language: str,
):
    farmer = supabase.table("farmers").insert({
            "farmer_id": str(uuid4()),
            "name": name,
            "mobile_no": mobile_no,
            "language": language,
        }).execute()
    if not farmer.data:
        return
    return Farmer(**farmer.data[0])

async def update_farmer(
    farmer_id: str,
    name: str,
    mobile_no: str,
    language: str,
    state: str,
    district: str,
):
    update_data = {}
    if name:
        update_data["name"] = name
    if mobile_no:
        update_data["mobile_no"] = mobile_no
    if language:
        update_data["language"] = language
    if state:
        update_data["state"] = state
    if district:
        update_data["district"] = district
    farmer = supabase.table("farmers").update(update_data).eq("farmer_id", farmer_id).execute()
    if not farmer.data:
        return
    return Farmer(**farmer.data[0])

async def create_farm(
    farmer_id: str,
    name: str,
    size: float,
    district: str,
    state: str,
    fcm_key: str,
):
    farm = supabase.table("farms").insert({
        "farm_id": str(uuid4()),
        "farmer_id": farmer_id,
        "farm_name": name,
        "size": size,
        "district": district,
        "state": state,
    }).execute()
    if not farm.data:
        return

    # check if present in locations table
    location = supabase.table("locations").select("*").eq("district", district).eq("state", state).execute()
    if not location.data:
        topic = f"weather_alerts_{district}_{state}"
        print(f"Creating location {district}, {state}, {topic}")
        await create_location(district, state, topic)
        # subscribe to topic
        print(f"Subscribing to topic {topic}")
        subscribe_to_topic(topic, [fcm_key])
    return Farm(**farm.data[0])

async def get_farmer(user_id: str):
    farmer = supabase.table("farmers").select("*").eq("farmer_id", user_id).execute()
    if not farmer.data:
        return

    farmer = Farmer(**farmer.data[0])
    return farmer

async def get_farms(farmer_id: str):
    farms = supabase.table("farms").select("*").eq("farmer_id", farmer_id).execute()
    if not farms.data:
        return
    return [Farm(**farm) for farm in farms.data]

async def create_location(
    district: str,
    state: str,
    firebase_topic: str,
):
    location = supabase.table("locations").insert({
        "id": str(uuid4()),
        "district": district,
        "state": state,
        "firebase_topic": firebase_topic,
    }).execute()
    return Location(**location.data[0])

async def get_all_locations() -> list[Location]:
    location = supabase.table("locations").select("*").execute()
    if not location.data:
        return
    return [Location(**location) for location in location.data]

async def create_crop(
    farm_id: str,
    crop_name: str,
    crop_variety: str,
    description: str,
    planted_at: datetime,
    previous_crop: str,
    previous_crop_yield: str,
):
    crop = supabase.table("crops").insert({
        "crop_id": str(uuid4()),
        "farm_id": farm_id,
        "crop_name": crop_name,
        "crop_variety": crop_variety,
        "description": description,
        "planted_at": str(planted_at),
        "previous_crop": previous_crop,
        "previous_crop_yield": previous_crop_yield,
    }).execute()
    if not crop.data:
        return
    return Crop(**crop.data[0])

async def get_crops(farmer_id: str):
    farms = supabase.table("farms").select("*").eq("farmer_id", farmer_id).execute()
    if not farms.data:
        return
    for farm in farms.data:
        farm = Farm(**farm)
        crops = supabase.table("crops").select("*").eq("farm_id", farm.farm_id).execute()
        if not crops.data:
            return
    return [Crop(**crop) for crop in crops.data]
    
