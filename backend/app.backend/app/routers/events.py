from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy.orm import Session
from app.deps import get_db, require_idempotency_key, claim_idempotency
from app.models import EngagementEvent

router = APIRouter()

class EngagementEventIn(BaseModel):
    stream_id: int
    viewer_id: int | None = None
    type: Literal["like","share","view"]
    flags: dict | None = Field(default=None)

@router.post("", status_code=201)
def create_event(payload: EngagementEventIn,
                 idem: str = Depends(require_idempotency_key),
                 db: Session = Depends(get_db)):
    claim_idempotency(db, idem, f"event:{payload.type}")
    row = EngagementEvent(
        stream_id=payload.stream_id,
        viewer_id=payload.viewer_id,
        type=payload.type,
        flags=payload.flags or {},
    )
    db.add(row); db.commit(); db.refresh(row)
    return {"ok": True, "event_id": row.id}
