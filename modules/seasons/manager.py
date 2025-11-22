from modules.shared.db import get_db_connection
from .models import SeasonCreate, SeasonUpdate

async def get_seasons():
    conn = await get_db_connection()
    try:
        seasons = await conn.fetch("""
            SELECT 
                s.season_id,
                s.league_id,
                s.season_name,
                s.start_date,
                s.end_date,
                l.league_name
            FROM seasons s
            LEFT JOIN leagues l ON s.league_id = l.league_id
            ORDER BY s.start_date DESC
        """)
        return [
            {
                "season_id": season["season_id"],
                "league_id": season["league_id"],
                "league_name": season["league_name"],
                "season_name": season["season_name"],
                "start_date": season["start_date"].isoformat() if season["start_date"] else None,
                "end_date": season["end_date"].isoformat() if season["end_date"] else None
            }
            for season in seasons
        ]
    finally:
        await conn.close()

async def get_season_by_id(season_id: int):
    conn = await get_db_connection()
    try:
        season = await conn.fetchrow("""
            SELECT 
                s.season_id,
                s.league_id,
                s.season_name,
                s.start_date,
                s.end_date,
                l.league_name
            FROM seasons s
            LEFT JOIN leagues l ON s.league_id = l.league_id
            WHERE s.season_id = $1
        """, season_id)
        
        if season:
            return {
                "season_id": season["season_id"],
                "league_id": season["league_id"],
                "league_name": season["league_name"],
                "season_name": season["season_name"],
                "start_date": season["start_date"].isoformat() if season["start_date"] else None,
                "end_date": season["end_date"].isoformat() if season["end_date"] else None
            }
        return None
    finally:
        await conn.close()

async def create_season(season_data: dict):
    conn = await get_db_connection()
    try:
        season_id = await conn.fetchval("""
            INSERT INTO seasons (league_id, season_name, start_date, end_date)
            VALUES ($1, $2, $3, $4) RETURNING season_id
        """, 
        season_data.get('league_id'),
        season_data.get('season_name'),
        season_data.get('start_date'),
        season_data.get('end_date'))
        return season_id
    finally:
        await conn.close()

async def update_season(season_id: int, season_data: dict):
    conn = await get_db_connection()
    try:
        result = await conn.execute("""
            UPDATE seasons 
            SET league_id = COALESCE($2, league_id),
                season_name = COALESCE($3, season_name),
                start_date = COALESCE($4, start_date),
                end_date = COALESCE($5, end_date)
            WHERE season_id = $1
        """, 
        season_id,
        season_data.get('league_id'),
        season_data.get('season_name'),
        season_data.get('start_date'),
        season_data.get('end_date'))
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_season(season_id: int):
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM seasons WHERE season_id = $1", season_id)
        return result == "DELETE 1"
    finally:
        await conn.close()
