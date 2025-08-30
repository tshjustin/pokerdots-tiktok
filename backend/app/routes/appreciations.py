# backend/routes/appreciations.py
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Video, TokenWallet, AppreciationToken
from ..appreciations.schemas import AppreciateIn, AppreciateOut, ErrorResponse
from ..auth.auth_utils import get_current_user  

router = APIRouter(prefix="/appreciations", tags=["Appreciations"])

# ---- CONFIG ----
MAX_PER_CREATOR_PER_MONTH = 10

# ---- helpers ----
def sha256_hex(ip: str) -> str:
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()

# ---- endpoints ----
@router.post(
    "",
    summary="Give an appreciation token to a video",
    description=(
        "Consumes 1 token from the viewer's wallet and records an appreciation for the video.\n\n"
        "**Rules enforced:**\n"
        "1. At most **one** appreciation per user per video (ever).\n"
        f"2. Per-creator monthly cap: **{MAX_PER_CREATOR_PER_MONTH}** per user.\n\n"
        "Monthly tokens are spent before bonus tokens."
    ),
    response_model=AppreciateOut,
    responses={
        200: {"description": "Recorded", "model": AppreciateOut},
        400: {"description": "Business rule violation", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        404: {"description": "Video or wallet not found", "model": ErrorResponse},
        409: {"description": "Already appreciated", "model": ErrorResponse},
    },
)
def appreciate(
    req: Request,
    body: AppreciateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),  # swap for your real dependency
):
    # 1) Load video + creator
    video = db.get(Video, body.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="video not found")
    if not video.creator_id:
        raise HTTPException(status_code=400, detail="video missing creator_id")

    # 2) Find user's wallet
    wallet = (
        db.query(TokenWallet)
          .filter(TokenWallet.user_id == user.id)
          .first()
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="wallet not found")

    # 3) Prevent duplicate appreciation (unique per wallet_id + video_id)
    dup = (
        db.query(AppreciationToken)
          .filter(
              AppreciationToken.wallet_id == wallet.wallet_id,
              AppreciationToken.video_id == video.id,
          )
          .first()
    )
    if dup:
        raise HTTPException(status_code=409, detail="already appreciated")

    # 4) Per-creator monthly cap (should we have a monthly cap?)
    month_count = (
        db.query(func.count(AppreciationToken.token_id))
          .join(Video, Video.id == AppreciationToken.video_id)
          .filter(
              AppreciationToken.wallet_id == wallet.wallet_id,
              Video.creator_id == video.creator_id,
              extract("year", AppreciationToken.created_at) == extract("year", func.now()),
              extract("month", AppreciationToken.created_at) == extract("month", func.now()),
          )
          .scalar()
    )
    if month_count >= MAX_PER_CREATOR_PER_MONTH:
        raise HTTPException(status_code=400, detail="monthly cap reached for this creator")

    # 5) Ensure wallet has tokens (monthly first, then bonus)
    monthly = wallet.monthly_budget or 0
    bonus = wallet.bonus_balance or 0
    if monthly + bonus < 1:
        raise HTTPException(status_code=400, detail="insufficient tokens")

    # 6) Record appreciation + deduct
    client_ip = req.headers.get("x-forwarded-for") or (req.client.host if req.client else "0.0.0.0")
    ip_hash = sha256_hex(client_ip)

    apprec = AppreciationToken(
        user_id=user.id,
        video_id=video.id,
        ip_hash=ip_hash,
        source=body.source.value if hasattr(body.source, "value") else body.source,
    )
    db.add(apprec)

    if monthly > 0:
        wallet.monthly_budget = monthly - 1
    else:
        wallet.bonus_balance = bonus - 1

    db.commit()
    db.refresh(wallet)

    return AppreciateOut(
        ok=True,
        remaining_tokens=(wallet.monthly_budget or 0) + (wallet.bonus_balance or 0),
        creator_monthly_count=month_count + 1,
        message="Appreciation recorded",
    )
