# backend/appreciations/schemas.py
from pydantic import BaseModel, Field
from enum import Enum as PyEnum

class AppreciationSourceEnum(str, PyEnum):
    tap = "tap"
    ad_boost = "ad_boost"

class AppreciateIn(BaseModel):
    video_id: int = Field(..., example=123, description="ID of the video to appreciate")
    source: AppreciationSourceEnum = Field(default=AppreciationSourceEnum.tap, example="tap")
    device_fingerprint: str | None = Field(default=None, example="abc123def456")
    user_id: int

class AppreciateOut(BaseModel):
    ok: bool = Field(True, example=True)
    remaining_tokens: int = Field(..., example=7, description="Total tokens left after deduction")
    creator_monthly_count: int = Field(..., example=3, description="How many appreciations you’ve given to this creator this month (including this one)")
    message: str = Field(..., example="Appreciation recorded")

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="insufficient tokens")
