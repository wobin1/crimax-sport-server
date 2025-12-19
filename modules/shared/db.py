import asyncpg
from fastapi import HTTPException
from .schema import CREATE_TABLES
from .migrations import run_all_migrations
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the src directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

async def get_db_connection():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

async def init_db():
    """Initialize database: create tables and run migrations"""
    conn = await get_db_connection()
    try:
        # Step 1: Create base tables
        logger.info("Creating base database tables...")
        await conn.execute(CREATE_TABLES)
        logger.info("✅ Base tables created successfully")
        
        # Step 2: Run all migrations
        await run_all_migrations(conn)
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await conn.close()