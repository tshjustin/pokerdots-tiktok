# backend/auth/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
import logging

from database.models import User, TokenWallet
from database.session import get_db
from .auth_utils import authenticate_user, create_access_token
from .schemas import CreateUserRequest, Token, Message, ErrorResponse

# ---------- logging ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- router & security ----------
router = APIRouter(prefix="/auth", tags=["Auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# IMPORTANT: make this the absolute path to match your route
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ---------- endpoints ----------
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Registers a new user with **username**, **email**, and **password**.",
    response_model=Message,
    responses={
        201: {"description": "User created", "model": Message},
        400: {"description": "Validation/constraint error", "model": ErrorResponse},
        409: {"description": "Duplicate username/email", "model": ErrorResponse},
        500: {"description": "Server error", "model": ErrorResponse},
    },
)
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
):
    try:
        # First, create user account to get user ID
        new_user = User(
            username=request.username,
            email=request.email,
            password_hash=bcrypt_context.hash(request.password),
        )
        db.add(new_user)
        db.flush() 
        # Then create wallet with the user ID
        new_wallet = TokenWallet(user_id = new_user.id)
        db.add(new_wallet)
        # Commit both wallet and user
        db.commit()
        # Return a concrete body so Swagger shows it
        return {"message": "User created"}

    except IntegrityError as ie:
        db.rollback()
        error_info = str(getattr(ie, "orig", ie)).lower()
        if "email" in error_info:
            logger.error("Email address is already registered!")
            # 409 is the conventional status for duplicates
            raise HTTPException(status_code=409, detail="Email address is already registered")
        if "username" in error_info:
            logger.error("Username is already registered!")
            raise HTTPException(status_code=409, detail="Username is already taken")
        raise HTTPException(status_code=400, detail="Integrity constraint violated")

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")

@router.post(
    "/token",
    summary="Get access token (OAuth2 Password)",
    description=(
        "Exchange **username**/**password** for a JWT access token.\n\n"
        "Then click **Authorize** (top-right in Swagger) and enter `Bearer <token>` "
        "to call protected endpoints."
    ),
    response_model=Token,
    responses={
        200: {"description": "Token issued", "model": Token},
        401: {"description": "Invalid credentials", "model": ErrorResponse},
        500: {"description": "Server error", "model": ErrorResponse},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code=401, detail="Could not validate user.")
        token = create_access_token(user)
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException as he:
        raise he
    
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=500, detail=f"An error has occurred: {e}")
