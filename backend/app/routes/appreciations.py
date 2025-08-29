# backend/routes/appreciations.py
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from database.session import get_db
from database import models
from ..appreciations.schemas import AppreciateIn, AppreciateOut, ErrorResponse  

router = APIRouter(prefix="/appreciations", tags=["Appreciations"])

# ---- CONFIG ----
MAX_PER_CREATOR_PER_MONTH = 10

# ---- AUTH (replace with your real dependency if you already have one) ----
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Placeholder for demo:
    - Treat the token as a username and load that user.
    Replace with your real JWT decoder + user lookup.
    """
    # >>> REPLACE THIS with your actual token decoding <<<
    user = db.query(models.User).filter(models.User.username == token).first()
    if not user:
        # If you’re using real JWTs, map sub->user here
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# ---- helpers ----
def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ---- endpoint ----
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
    user: models.User = Depends(get_current_user),  # swap for your real dependency
):
    # 1) load video + creator
    video = db.get(models.Video, body.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="video not found")
    if not video.creator_id:
        raise HTTPException(status_code=400, detail="video missing creator_id")

    # 2) find user's wallet
    wallet = (
        db.query(models.TokenWallet)
          .filter(models.TokenWallet.user_id == user.id)
          .first()
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="wallet not found")

    # 3) prevent duplicate appreciation (unique per wallet_id + video_id)
    dup = (
        db.query(models.AppreciationToken)
          .filter(
              models.AppreciationToken.wallet_id == wallet.wallet_id,
              models.AppreciationToken.video_id == video.id,
          )
          .first()
    )
    if dup:
        raise HTTPException(status_code=409, detail="already appreciated")

    # 4) per-creator monthly cap
    month_count = (
        db.query(func.count(models.AppreciationToken.token_id))
          .join(models.Video, models.Video.id == models.AppreciationToken.video_id)
          .filter(
              models.AppreciationToken.wallet_id == wallet.wallet_id,
              models.Video.creator_id == video.creator_id,
              extract("year", models.AppreciationToken.created_at) == extract("year", func.now()),
              extract("month", models.AppreciationToken.created_at) == extract("month", func.now()),
          )
          .scalar()
    )
    if month_count >= MAX_PER_CREATOR_PER_MONTH:
        raise HTTPException(status_code=400, detail="monthly cap reached for this creator")

    # 5) ensure wallet has tokens (monthly first, then bonus)
    monthly = wallet.monthly_budget or 0
    bonus = wallet.bonus_balance or 0
    if monthly + bonus < 1:
        raise HTTPException(status_code=400, detail="insufficient tokens")

    # 6) record appreciation + deduct
    client_ip = req.headers.get("x-forwarded-for") or (req.client.host if req.client else "0.0.0.0")
    ip_hash = sha256_hex(client_ip)

    apprec = models.AppreciationToken(
        wallet_id=wallet.wallet_id,
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
