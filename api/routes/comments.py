from fastapi import APIRouter, HTTPException
from lib.db import create_comment, delete_comment, get_comments_for_post
from api.models.requests import CreateCommentRequest, DeleteCommentRequest

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/create")
async def create(comment: CreateCommentRequest):
    created_comment = await create_comment(
        comment.post_id,
        comment.user_id,
        comment.content
    )
    if not created_comment:
        raise HTTPException(status_code=400, detail="Failed to create comment. Post may not exist.")
    return created_comment

@router.delete("/delete/{comment_id}")
async def delete(comment_id: str, user_id: str):
    success = await delete_comment(comment_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found or you don't have permission to delete it")
    return {"message": "Comment deleted successfully"}

@router.get("/post/{post_id}")
async def get_post_comments(post_id: str, limit: int = 50, offset: int = 0):
    comments = await get_comments_for_post(post_id, limit, offset)
    return {"comments": comments, "count": len(comments)}
