from modules.shared.db import get_db_connection
from .models import VenueCreate, VenueUpdate

async def get_venues():
    conn = await get_db_connection()
    try:
        venues = await conn.fetch("SELECT * FROM venues ORDER BY venue_name")
        return [dict(venue) for venue in venues]
    finally:
        await conn.close()

async def get_venue_by_id(venue_id: int):
    conn = await get_db_connection()
    try:
        venue = await conn.fetchrow("SELECT * FROM venues WHERE venue_id = $1", venue_id)
        if venue:
            return dict(venue)
        return None
    finally:
        await conn.close()

async def create_venue(venue: VenueCreate):
    conn = await get_db_connection()
    try:
        venue_id = await conn.fetchval("""
            INSERT INTO venues (venue_name, address, capacity)
            VALUES ($1, $2, $3) RETURNING venue_id
        """, venue.venue_name, venue.address, venue.capacity)
        return venue_id
    finally:
        await conn.close()

async def update_venue(venue_id: int, venue: VenueUpdate):
    conn = await get_db_connection()
    try:
        result = await conn.execute("""
            UPDATE venues 
            SET venue_name = COALESCE($2, venue_name),
                address = COALESCE($3, address),
                capacity = COALESCE($4, capacity)
            WHERE venue_id = $1
        """, venue_id, venue.venue_name, venue.address, venue.capacity)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_venue(venue_id: int):
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM venues WHERE venue_id = $1", venue_id)
        return result == "DELETE 1"
    finally:
        await conn.close()
