import psycopg2
import os, logging
from dotenv import load_dotenv
from database.session import engine
from database import models

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOCAL_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")

def create_database():
    try:
        # Connect to local db
        conn = psycopg2.connect(LOCAL_DATABASE_URL)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT datname FROM pg_database WHERE datname='postgres'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("CREATE DATABASE postgres")
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise

def create_tables():
    # First, create the vector extension
    # with engine.connect() as connection:
    #     connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    #     connection.commit()
    
    # Then create all tables
    models.Base.metadata.create_all(bind=engine)
    
    # Explicitly alter the column type to ensure it's a vector
    # with engine.connect() as connection:
    #     try:
    #         # This ensures the column is properly recognized as a vector type
    #         connection.execute(text("""
    #             ALTER TABLE question_embeddings 
    #             ALTER COLUMN embedding TYPE vector(384) USING embedding::vector(384)
    #         """))
    #         connection.commit()
    #     except Exception as e:
    #         print(f"Error altering column type: {e}")
    
    # # Now create the HNSW index
    # with engine.connect() as connection:
    #     try:
    #         connection.execute(text("""
    #             CREATE INDEX IF NOT EXISTS question_embeddings_hnsw_idx 
    #             ON question_embeddings USING hnsw (embedding vector_cosine_ops) 
    #             WITH (m = 16, ef_construction = 64)
    #         """))
    #         connection.commit()
    #     except Exception as e:
    #         print(f"Error creating index: {e}")