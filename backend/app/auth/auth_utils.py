from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os, logging
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database.models import User
from passlib.context import CryptContext
from database.session import get_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

# Environment variables for security
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(user: User):
    """
    Generates an access token with expiration.
    """
    to_encode = {"sub": user.username, "id": user.id}
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticate users by checking if the username and password hash matches a record in the database
    """
    try:
        # Check if account with username exists
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        # Check if password hash matches the one in DB
        if not bcrypt_context.verify(password, user.password_hash):
            return False

        # Authentication success
        return user
    
    except Exception as e:
        logger.error(f"An error has occurred while authenticating user: {str(e)}")
        raise

def get_current_user(
    token: str = Depends(oauth2_bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError("Invalid token payload")
        
        # Get user by username (might replace this with an imported function)
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail=f"Could not validate credentials",
            )
        return user
    
    except HTTPException as he:
        raise he
    
    except Exception as e:
        logger.error(f"An error has occurred: {str(e)}")
