from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, conint
from sqlalchemy.orm import Session
from app.deps import get_db, require_idempotency_key, claim_idempotency, get_client_ip, hash_ip
from app.models import Gift

router = APIRouter()

class GiftIn(BaseModel):
    stream_id: int
    from_user: int
    coin_amount: conint(strict=True, gt=0)
    device_fingerprint_hash: str | None = None

@router.post("", status_code=201)
def send_gift(payload: GiftIn,
              request: Request,
              idem: str = Depends(require_idempotency_key),
              db: Session = Depends(get_db)):
    claim_idempotency(db, idem, "gift")
    ip = get_client_ip(request)
    row = Gift(
        stream_id=payload.stream_id,
        from_user=payload.from_user,
        coin_amount=payload.coin_amount,
        device_fingerprint_hash=payload.device_fingerprint_hash,
        ip_hash=hash_ip(ip),
    )
    db.add(row); db.commit(); db.refresh(row)
    return {"ok": True, "gift_id": row.id}
