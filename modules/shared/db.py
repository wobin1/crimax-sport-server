import asyncpg
from fastapi import HTTPException
from .schema import CREATE_TABLES

DATABASE_URL = "postgresql://postgres:password@localhost:5432/crimax_sport_db"

async def get_db_connection():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

async def init_db():
    conn = await get_db_connection()
    try:
        await conn.execute(CREATE_TABLES)
    finally:
        await conn.close()