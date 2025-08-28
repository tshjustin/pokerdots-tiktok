from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from datetime import timedelta
import logging
from database.models import User
from database.session import SessionLocal
from .auth_utils import authenticate_user, create_access_token
from .schemas import CreateUserRequest, Token

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up router
router = APIRouter(prefix="/auth", tags=["auth"])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest, 
    db: Session = Depends(get_db)):
    try:
        # Create new user obj
        new_user = User(
            username=request.username,
            email=request.email,
            password_hash=bcrypt_context.hash(request.password),
        )
        # Commit to DB
        db.add(new_user)
        db.commit()

    except IntegrityError as ie:
        db.rollback()
        error_info = str(e.orig).lower()
        if "email" in error_info:
            logger.error("Email address is already registered!")
            raise HTTPException(
                status_code=400,
                detail="Email address is already registered"
            )
        elif "username" in error_info:
            logger.error("Username is already registered!")
            raise HTTPException(
                status_code=400,
                detail="Username is already taken"
            )

    except Exception as e:
        db.rollback()
        logger.error(f"An error has occurred while creating new user account: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error has occurred while creating new user account: {str(e)}")
    
@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)):
        try:
            user = authenticate_user(form_data.username, form_data.password, db)
            # Handle auth fail
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Could not validate user.",
                )
            
            # Create user token
            token = create_access_token(user)

            return {"access_token": token, "token_type": "bearer"}
        
        except HTTPException as he:
            # Raise HTTPException as it is
            raise he
        
        except Exception as e:
            logger.error(f"An error has occurred: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"An error has occurred: {str(e)}",
            )
