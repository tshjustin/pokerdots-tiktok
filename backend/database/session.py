from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging, os
from dotenv import load_dotenv
load_dotenv()

LOCAL_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")

# Initialize DB engine
engine = create_engine(
    LOCAL_DATABASE_URL,
    pool_size=100,
    max_overflow=10,
    pool_timeout=30,
    # echo=True, # prints out the SQL query  
)

# Initialize DB session instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
