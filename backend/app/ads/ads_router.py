from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.session import get_db
from database.models import User, Ad, AdSession, TokenWallet
from ..auth.auth_utils import get_current_user
import logging, secrets
from datetime import datetime, UTC
from .schemas import AdStartRequest, AdStartResponse, AdCompleteRequest, AdCompleteResponse

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up router
router = APIRouter(prefix="/ads", tags=["Ads"])

# Endpoints
@router.post("/start_ad_watch")
async def start_ad_watch(
    request: AdStartRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start watching an ad - creates a session token"""
    # Validate ad exists
    ad = db.query(Ad).filter(Ad.ad_id == request.ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Check if user already has an incomplete session for this ad
    existing_session = (
        db.query(AdSession)
        .filter(
            AdSession.user_id == request.user_id, 
            AdSession.ad_id == request.ad_id, 
            AdSession.is_completed == False
        ).first()
    )
    if existing_session:
        raise HTTPException(status_code=400, detail="Already watching this ad")

    try:
        # Create new ad session
        session_token = secrets.token_urlsafe(32)
        ad_session = AdSession(
            user_id=request.user_id,
            ad_id=request.ad_id,
            session_token=session_token,
        )

        db.add(ad_session)
        db.commit()
        db.refresh(ad_session)

        return AdStartResponse(
            session_token=session_token,
            ad_duration=ad.duration,
            message="Ad session started"
        )

    except HTTPException as he:
        raise he

    except Exception as e:
        db.rollback()
        logger.error(f"An error has occurred while starting ad session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error has occurred while starting ad session: {str(e)}"
        )
    
@router.post("/complete_ad_watch")
async def complete_ad_watch(
    request: AdCompleteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete ad watch and grant appreciation token"""
    ad_session = (
        db.query(AdSession)
        .filter(
            AdSession.session_token == request.session_token,
            AdSession.is_completed == False
        ).first()
    )
    if not ad_session:
        raise HTTPException(status_code=404, detail="Invalid session token or ad already completed")
    
    try:
        # Mark session as complete
        ad_session.is_completed = True
        ad_session.completed_at = datetime.now(UTC)

        # Get user wallet
        wallet = db.query(TokenWallet).filter(TokenWallet.user_id == request.user_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Add appreciation token to wallet
        wallet.bonus_balance += 1

        db.commit()
        db.refresh(ad_session)
        db.refresh(wallet)

        return AdCompleteResponse(
            balance=wallet.bonus_balance+wallet.monthly_budget,
            message="Wallet top up successfully"
        )
    
    except HTTPException as he:
        raise he
    
    except Exception as e:
        db.rollback()
        logger.error(f"An error has occurred while topping up wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error has occurred while topping up wallet: {str(e)}")
