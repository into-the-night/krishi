import json
import numpy as np
from uuid import uuid4
from datetime import datetime
from supabase import AsyncClient, create_async_client

from config.settings import settings
from lib.firebase import subscribe_to_topic
from lib.models import Location, Farmer, Crop, Farm, Post, Comment, Message

global supabase 
supabase = None

async def initialize_supabase():
    """Initialize the Supabase client asynchronously."""
    global supabase
    if supabase is None:
        supabase = await create_async_client(
            settings.supabase_uri, settings.supabase_service_key
        )
    return supabase

async def get_supabase_client() -> AsyncClient:
    """Get the Supabase client, initializing it if necessary."""
    global supabase
    if supabase is None:
        await initialize_supabase()
    return supabase

async def create_presigned_url(file_id: str, expires_in: int = 360):
    supabase = await get_supabase_client()
    response = (
        await supabase.storage
        .from_("krishi")
        .create_signed_url(file_id, expires_in)
    )
    return response['signedURL']

##### FARMER OPERATIONS #####

async def create_farmer(
    name: str,
    mobile_no: str,
    language: str,
):
    supabase = await get_supabase_client()
    farmer = await supabase.table("farmers").insert({
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
    supabase = await get_supabase_client()
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
    farmer = await supabase.table("farmers").update(update_data).eq("farmer_id", farmer_id).execute()
    if not farmer.data:
        return
    return Farmer(**farmer.data[0])

async def get_farmer(user_id: str):
    supabase = await get_supabase_client()
    farmer = await supabase.table("farmers").select("*").eq("farmer_id", user_id).execute()
    if not farmer.data:
        return

    farmer = Farmer(**farmer.data[0])
    return farmer

async def get_all_languages():
    supabase = await get_supabase_client()
    languages = await (
        supabase
        .table("farmers")
        .select("language")
        .distinct()
        .execute()
    )
    if not languages.data:
        return
    return [language["language"] for language in languages.data]

##### FARM OPERATIONS #####

async def create_farm(
    farmer_id: str,
    name: str,
    size: float,
    district: str,
    state: str,
    fcm_key: str,
):
    supabase = await get_supabase_client()
    farm = await supabase.table("farms").insert({
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
    location = await supabase.table("locations").select("*").eq("district", district).eq("state", state).execute()
    if not location.data:
        topic = f"weather_alerts_{district}_{state}"
        print(f"Creating location {district}, {state}, {topic}")
        await create_location(district, state, topic)
        # subscribe to topic
        print(f"Subscribing to topic {topic}")
        subscribe_to_topic(topic, [fcm_key])
    return Farm(**farm.data[0])

async def get_farms(farmer_id: str):
    supabase = await get_supabase_client()
    farms = await supabase.table("farms").select("*").eq("farmer_id", farmer_id).execute()
    if not farms.data:
        return
    return [Farm(**farm) for farm in farms.data]

##### LOCATION OPERATIONS #####

async def create_location(
    district: str,
    state: str,
    firebase_topic: str,
):
    supabase = await get_supabase_client()
    location = await supabase.table("locations").insert({
        "id": str(uuid4()),
        "district": district,
        "state": state,
        "firebase_topic": firebase_topic,
    }).execute()
    return Location(**location.data[0])

async def get_all_locations() -> list[Location]:
    supabase = await get_supabase_client()
    location = await supabase.table("locations").select("*").execute()
    if not location.data:
        return
    return [Location(**location) for location in location.data]


##### CROP OPERATIONS #####

async def create_crop(
    farm_id: str,
    crop_name: str,
    crop_variety: str,
    description: str,
    planted_at: datetime,
    previous_crop: str,
    previous_crop_yield: str,
):
    supabase = await get_supabase_client()
    crop = await supabase.table("crops").insert({
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
    supabase = await get_supabase_client()
    farms = await supabase.table("farms").select("*").eq("farmer_id", farmer_id).execute()
    if not farms.data:
        return
    for farm in farms.data:
        farm = Farm(**farm)
        crops = await supabase.table("crops").select("*").eq("farm_id", farm.farm_id).execute()
        if not crops.data:
            return
    return [Crop(**crop) for crop in crops.data]

##### POST OPERATIONS #####

async def create_post(
    user_id: str,
    content_url: str,
    content_desc: str,
):
    supabase = await get_supabase_client()
    post = await supabase.table("posts").insert({
        "id": str(uuid4()),
        "user_id": user_id,
        "content_url": content_url,
        "content_desc": content_desc,
        "likes": 0,
        "reports": 0,
        "comment_ids": [],
    }).execute()
    if not post.data:
        return
    return Post(**post.data[0])

async def delete_post(post_id: str, user_id: str):
    supabase = await get_supabase_client()
    # First check if the post belongs to the user
    post = await supabase.table("posts").select("*").eq("id", post_id).eq("user_id", user_id).execute()
    if not post.data:
        return False
    
    # Delete the post
    result = await supabase.table("posts").delete().eq("id", post_id).execute()
    return True if result.data else False

async def get_all_posts(limit: int = 50, offset: int = 0):
    supabase = await get_supabase_client()
    posts = await supabase.table("posts").select("*").order("created_at", desc=True).limit(limit).offset(offset).execute()
    if not posts.data:
        return []
    return [Post(**post) for post in posts.data]

async def like_post(post_id: str):
    supabase = await get_supabase_client()
    # Get current likes count
    post = await supabase.table("posts").select("likes").eq("id", post_id).execute()
    if not post.data:
        return False  # Post not found
    
    current_likes = post.data[0]["likes"]
    # Increment likes count
    result = await supabase.table("posts").update({"likes": current_likes + 1}).eq("id", post_id).execute()
    return True if result.data else False

async def dislike_post(post_id: str):
    supabase = await get_supabase_client()
    # Get current likes count
    post = await supabase.table("posts").select("likes").eq("id", post_id).execute()
    if not post.data:
        return False  # Post not found
    
    current_likes = post.data[0]["likes"]
    # Decrement likes count (but not below 0)
    result = await supabase.table("posts").update({"likes": max(0, current_likes - 1)}).eq("id", post_id).execute()
    return True if result.data else False

async def add_post_translation(post_id: str, language: str, translation: str):
    supabase = await get_supabase_client()
    post = await supabase.table("posts").select("content_desc").eq("id", post_id).execute()
    if not post.data:
        return False  # Post not found
    
    content_desc = json.loads(post.data[0]["content_desc"])
    content_desc["translations"][language] = translation
    await supabase.table("posts").update({"content_desc": json.dumps(content_desc)}).eq("id", post_id).execute()
    return True

##### COMMENT OPERATIONS #####

async def create_comment(post_id: str, user_id: str, content: str):
    try:
        supabase = await get_supabase_client()
        # First check if post exists
        post = await supabase.table("posts").select("comment_ids").eq("id", post_id).execute()
        if not post.data:
            return None  # Post not found
        
        # Create the comment
        comment_data = {
            "user_id": user_id,
            "content": content,
            "likes": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        comment_result = await supabase.table("comments").insert(comment_data).execute()
        if not comment_result.data:
            return None
        
        comment = comment_result.data[0]
        comment_id = comment["id"]
        
        # Update the post's comment_ids array
        current_comment_ids = post.data[0]["comment_ids"] or []
        current_comment_ids.append(comment_id)
        
        await supabase.table("posts").update({"comment_ids": current_comment_ids}).eq("id", post_id).execute()
        
        return Comment(**comment)
    except Exception as e:
        print(f"Error creating comment: {e}")
        return None

async def delete_comment(comment_id: str, user_id: str):
    try:
        supabase = await get_supabase_client()
        # First check if comment exists and belongs to user
        comment = await supabase.table("comments").select("*").eq("id", comment_id).eq("user_id", user_id).execute()
        if not comment.data:
            return False  # Comment not found or not owned by user
        
        # Find the post that contains this comment
        posts = await supabase.table("posts").select("id, comment_ids").contains("comment_ids", [comment_id]).execute()
        
        if posts.data:
            for post in posts.data:
                # Remove comment_id from the post's comment_ids array
                updated_comment_ids = [cid for cid in post["comment_ids"] if cid != comment_id]
                await supabase.table("posts").update({"comment_ids": updated_comment_ids}).eq("id", post["id"]).execute()
        
        # Delete the comment
        result = await supabase.table("comments").delete().eq("id", comment_id).eq("user_id", user_id).execute()
        return True if result.data else False
    except Exception as e:
        print(f"Error deleting comment: {e}")
        return False

async def get_comments_for_post(post_id: str, limit: int = 50, offset: int = 0):
    try:
        supabase = await get_supabase_client()
        # Get comment IDs from the post
        post = await supabase.table("posts").select("comment_ids").eq("id", post_id).execute()
        if not post.data or not post.data[0]["comment_ids"]:
            return []
        
        comment_ids = post.data[0]["comment_ids"]
        
        # Fetch comments by IDs, ordered by creation date
        for comment_id in comment_ids:
            comments = await supabase.table("comments")\
                .select("*")\
                    .eq("id", comment_id)\
                    .order("created_at", desc=True)\
                .execute()
        
        if not comments.data:
            return []
        
        return [Comment(**comment) for comment in comments.data]
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

##### STORAGE OPERATIONS #####

async def save_to_supabase(file_path: str, file_id: str, content_type: str) -> str:
    """Save file to supabase
    
    Args:
        file_path (str): path to the file
        file_id (str): unique identifier for the file in supabase
        content_type (str): content type of the file (e.g., "audio/x-wav" or "image/jpeg") defaults to "text/html"
    """
    supabase = await get_supabase_client()

    with open(file_path, "rb") as f:
        response = (
            await supabase.storage
            .from_("krishi")
            .upload(
                file=f,
                path=file_id,
                file_options={"cache-control": "3600", "upsert": "false", "content-type": content_type},
            )
        )
    if not response:
        return
    return True


##### MESSAGE OPERATIONS #####

async def create_message(user_id: str, message_id: str, role: str, content: str, content_type: str):
    supabase = await get_supabase_client()
    message = await supabase.table("messages").insert({
        "id": message_id,
        "user_id": user_id,
        "role": role,
        "content": content,
        "content_type": content_type,
    }).execute()
    if not message.data:
        return
    return Message(**message.data[0])

async def get_messages(user_id: str, limit: int = 50, offset: int = 0):
    supabase = await get_supabase_client()
    messages = await (
        supabase
        .table("messages")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .offset(offset)
    ).execute()

    if not messages.data:
        return []
    return [Message(**message) for message in messages.data]

async def get_message(message_id: str, content_type: str = None):
    
    try:
        supabase = await get_supabase_client()
        message = await (
            supabase
            .table("messages")
            .select("*")
            .eq("id", message_id)
            .eq("content_type", content_type)
        ).execute()
        
        if not message.data:
            return False
        return Message(**message.data[0])
    except Exception as e:
        print(f"Error getting message: {e}")
        return False