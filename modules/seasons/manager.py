# filepath: /Applications/wobin/crimax/crimax_sport/crimax_sport_server/src/modules/seasons/manager.py
from modules.shared.db import get_db_connection
from typing import Optional
from datetime import datetime
import json

async def get_seasons():
    """Get all seasons with league information"""
    conn = await get_db_connection()
    try:
        seasons = await conn.fetch("""
            SELECT 
                s.season_id,
                s.season_name,
                s.start_date,
                s.end_date,
                s.league_id,
                l.league_name
            FROM seasons s
            LEFT JOIN leagues l ON s.league_id = l.league_id
            ORDER BY s.start_date DESC
        """)
        return [
            {
                "season_id": season["season_id"],
                "season_name": season["season_name"],
                "start_date": season["start_date"].isoformat() if season["start_date"] else None,
                "end_date": season["end_date"].isoformat() if season["end_date"] else None,
                "league_id": season["league_id"],
                "league_name": season["league_name"]
            }
            for season in seasons
        ]
    finally:
        await conn.close()

async def get_season_by_id(season_id: int):
    """Get a specific season by ID"""
    conn = await get_db_connection()
    try:
        season = await conn.fetchrow("""
            SELECT 
                s.season_id,
                s.season_name,
                s.start_date,
                s.end_date,
                s.league_id,
                l.league_name
            FROM seasons s
            LEFT JOIN leagues l ON s.league_id = l.league_id
            WHERE s.season_id = $1
        """, season_id)

        if season:
            return {
                "season_id": season["season_id"],
                "season_name": season["season_name"],
                "start_date": season["start_date"].isoformat() if season["start_date"] else None,
                "end_date": season["end_date"].isoformat() if season["end_date"] else None,
                "league_id": season["league_id"],
                "league_name": season["league_name"]
            }
        else:
            return None
    finally:
        await conn.close()

async def create_season(season_data: dict):
    """Create a new season"""
    conn = await get_db_connection()
    try:
        # Parse date strings to date objects
        start_date = datetime.strptime(season_data.get("start_date"), "%Y-%m-%d").date() if season_data.get("start_date") else None
        end_date = datetime.strptime(season_data.get("end_date"), "%Y-%m-%d").date() if season_data.get("end_date") else None
        
        season_id = await conn.fetchval("""
            INSERT INTO seasons (season_name, start_date, end_date, league_id)
            VALUES ($1, $2, $3, $4) RETURNING season_id
        """, season_data.get("season_name"), start_date, end_date, season_data.get("league_id"))
        return season_id
    finally:
        await conn.close()

async def update_season(season_id: int, season_data: dict):
    """Update an existing season"""
    conn = await get_db_connection()
    try:
        # Parse date strings to date objects if present
        start_date = datetime.strptime(season_data.get("start_date"), "%Y-%m-%d").date() if season_data.get("start_date") else None
        end_date = datetime.strptime(season_data.get("end_date"), "%Y-%m-%d").date() if season_data.get("end_date") else None
        
        result = await conn.execute("""
            UPDATE seasons 
            SET season_name = COALESCE($2, season_name),
                start_date = COALESCE($3, start_date),
                end_date = COALESCE($4, end_date),
                league_id = COALESCE($5, league_id)
            WHERE season_id = $1
        """, season_id, season_data.get("season_name"), start_date, end_date, season_data.get("league_id"))
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_season(season_id: int):
    """Delete a season"""
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM seasons WHERE season_id = $1", season_id)
        return result == "DELETE 1"
    finally:
        await conn.close()
