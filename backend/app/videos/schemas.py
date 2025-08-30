from pydantic import BaseModel, Field
from datetime import datetime

class VideoUploadRequest(BaseModel):
    title: str = Field(..., max_length=100)
    description: str | None = Field(None, max_length=500)

class VideoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    creator_id: int
    creator_username: str | None
    duration_s: int | None
    view_count: int
    ai_score: float | None
    ai_label: str | None
    created_at: datetime

class VideoUploadResponse(BaseModel):
    video_id: int
    title: str
    message: str = "video uploaded successfully"