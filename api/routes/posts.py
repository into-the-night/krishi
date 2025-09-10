from fastapi import APIRouter, HTTPException
from lib.db import create_post, delete_post, get_all_posts, like_post, dislike_post
from api.models.requests import CreatePostRequest, LikeDislikePostRequest

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/create")
async def create(post: CreatePostRequest):
    created_post = await create_post(
        post.user_id,
        post.content_url,
        post.content_desc,
    )
    if not created_post:
        raise HTTPException(status_code=400, detail="Failed to create post")
    return created_post

@router.delete("/delete/{post_id}")
async def delete(post_id: str, user_id: str):
    success = await delete_post(post_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found or you don't have permission to delete it")
    return {"message": "Post deleted successfully"}

@router.get("/feed")
async def get_feed(limit: int = 50, offset: int = 0):
    posts = await get_all_posts(limit, offset)
    return {"posts": posts, "count": len(posts)}

@router.post("/like")
async def like(request: LikeDislikePostRequest):
    success = await like_post(request.post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post liked successfully"}

@router.post("/dislike")
async def dislike(request: LikeDislikePostRequest):
    success = await dislike_post(request.post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post disliked successfully"}