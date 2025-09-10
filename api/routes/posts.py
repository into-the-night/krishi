from fastapi import APIRouter, HTTPException
from lib.db import create_post, delete_post, get_all_posts, like_post, dislike_post
from api.models.requests import CreatePostRequest, LikeDislikePostRequest
from api.models.responses import PostResponse, PostDeleteResponse, PostFeedResponse, PostActionResponse
from agent.bot import Bot

router = APIRouter(prefix="/posts", tags=["posts"])
bot = Bot()

@router.post("/create", response_model=PostResponse)
async def create(post: CreatePostRequest) -> PostResponse:
    created_post = await create_post(
        post.user_id,
        post.content_url,
        post.content_desc,
    )
    if not created_post:
        raise HTTPException(status_code=400, detail="Failed to create post")
    return created_post

@router.delete("/delete/{post_id}", response_model=PostDeleteResponse)
async def delete(post_id: str, user_id: str) -> PostDeleteResponse:
    success = await delete_post(post_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found or you don't have permission to delete it")
    return PostDeleteResponse(message="Post deleted successfully")

@router.get("/feed", response_model=PostFeedResponse)
async def get_feed(limit: int = 50, offset: int = 0, language: str = "en") -> PostFeedResponse:
    posts = await get_all_posts(limit, offset)
    for post in posts:
        post.content_desc = bot.translate_content(post.content_desc, language)
    return PostFeedResponse(posts=posts, count=len(posts))

@router.post("/like", response_model=PostActionResponse)
async def like(request: LikeDislikePostRequest) -> PostActionResponse:
    success = await like_post(request.post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostActionResponse(message="Post liked successfully")

@router.post("/dislike", response_model=PostActionResponse)
async def dislike(request: LikeDislikePostRequest) -> PostActionResponse:
    success = await dislike_post(request.post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostActionResponse(message="Post disliked successfully")