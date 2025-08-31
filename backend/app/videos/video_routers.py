from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.session import get_db
from database.models import Video, User
from ..auth.auth_utils import get_current_user
from ..storage.s3_client import upload_video_to_s3, generate_presigned_url

from ..services.video_inference import trigger_analysis

from .schemas import VideoUploadResponse, VideoResponse

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # validate file type
    if not file.filename.lower().endswith('.mp4'):
        raise HTTPException(400, "only .mp4 supported")
    
    file_content = await file.read()
    
    try:
        # updated to get s3 url 
        s3_key, s3_url = await upload_video_to_s3(file_content, file.filename, user.id)
        
        # Create video record with both s3_key and s3_url
        video = Video(
            creator_id=user.id,
            title=title,
            description=description,
            s3_key=s3_key,
            s3_url=s3_url,
            file_size=len(file_content),
            upload_status="completed"
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        await trigger_analysis(video.id)

        return VideoUploadResponse(
            video_id=video.id,
            title=video.title
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"upload failed {str(e)}")

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).join(User).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "video not found")
    
    return VideoResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        creator_id=video.creator_id,
        creator_username=video.creator.username,
        duration_s=video.duration_s,
        view_count=video.view_count,
        ai_score=video.ai_score,
        ai_label=video.ai_label,
        created_at=video.created_at
    )

@router.get("/{video_id}/url")
def get_video_url(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "video not found")
    
    return {
        "video_id": video.id,
        "s3_url": video.s3_url, 
        "presigned_url": generate_presigned_url(video.s3_key)  # temporary URL if needed
    }

@router.get("/{video_id}/ai-status")
def get_ai_status(video_id: int, db: Session = Depends(get_db)):
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(404, "vid not found")
    
    return {
        "video_id": video.id,
        "ai_status": video.ai_status,
        "ai_score": video.ai_score,
        "ai_label": video.ai_label,
        "genuinity_score": video.genuinity_score
    }