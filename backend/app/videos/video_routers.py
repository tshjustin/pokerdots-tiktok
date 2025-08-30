from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from sqlalchemy.orm import Session
from database.session import get_db
from database.models import Video, User

from ..auth.auth_utils import get_current_user # TODO: get the current user 

from ..storage.s3_client import upload_video_to_s3, generate_presigned_url
from .schemas import VideoUploadResponse, VideoResponse

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),  # AUTH REQUIRED
    db: Session = Depends(get_db)
):
    # check for .mp4 
    if not file.filename.lower().endswith(('.mp4')):
        raise HTTPException(400, "only .mp4 supported")
    
    file_content = await file.read()
    
    try:
        s3_key = await upload_video_to_s3(file_content, file.filename, user.id)
        
        video = Video(
            creator_id=user.id,
            title=title,
            description=description,
            s3_key=s3_key,
            file_size=len(file_content),
            upload_status="completed"
        )
        
        # add meta data to database 
        db.add(video)
        db.commit()
        db.refresh(video)
        
        return VideoUploadResponse(
            video_id=video.id,
            title=video.title,
            s3_key=s3_key
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"upload failed {str(e)}")

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).join(User).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "video not found")
    
    # url for video access 
    video_url = generate_presigned_url(video.s3_key)
    
    return VideoResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        creator_username=video.creator.username,
        video_url=video_url,  # fix this if needed 
        duration_s=video.duration_s,
        view_count=video.view_count,
        created_at=video.created_at
    )