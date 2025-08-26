from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.deps import get_db, get_client_ip, hash_ip
from app.models import ViewerSession

router = APIRouter()

class SessionStartIn(BaseModel):
    stream_id: int
    viewer_id: int | None = None
    device_fingerprint_hash: str | None = None

@router.post("/start")
def start_session(payload: SessionStartIn, request: Request, db: Session = Depends(get_db)):
    ip = get_client_ip(request)
    vs = ViewerSession(
        stream_id=payload.stream_id,
        viewer_id=payload.viewer_id,
        ip_hash=hash_ip(ip),
        device_fingerprint_hash=payload.device_fingerprint_hash,
    )
    db.add(vs)
    db.commit()
    db.refresh(vs)
    return {"status": "started", "session_id": vs.id}

class SessionEndIn(BaseModel):
    session_id: int

@router.post("/end")
def end_session(payload: SessionEndIn, db: Session = Depends(get_db)):
    vs = db.get(ViewerSession, payload.session_id)
    if not vs:
        return {"status": "not_found"}
    from sqlalchemy import text
    db.execute(text("UPDATE viewer_sessions SET ended_at = now() WHERE id = :id"), {"id": payload.session_id})
    db.commit()
    return {"status": "ended"}
