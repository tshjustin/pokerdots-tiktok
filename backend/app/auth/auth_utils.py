from jose import JWTError, jwt
import os, logging
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database.models import User
from passlib.context import CryptContext

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

