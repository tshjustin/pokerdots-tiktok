from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.deps import get_db, require_idempotency_key, claim_idempotency
from app.models import Comment

router = APIRouter()

class CommentIn(BaseModel):
    stream_id: int
    viewer_id: int | None = None
    text: str

@router.post("", status_code=201)
def post_comment(payload: CommentIn,
                 idem: str = Depends(require_idempotency_key),
                 db: Session = Depends(get_db)):
    claim_idempotency(db, idem, "comment")
    row = Comment(stream_id=payload.stream_id, viewer_id=payload.viewer_id, text=payload.text, flags={})
    db.add(row); db.commit(); db.refresh(row)
    return {"ok": True, "comment_id": row.id}
