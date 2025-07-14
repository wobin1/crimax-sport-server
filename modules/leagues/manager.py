from modules.shared.db import get_db_connection
from .models import LeagueCreate
import json

async def get_leagues():
    conn = await get_db_connection()
    try:
        leagues = await conn.fetch("SELECT * FROM leagues")
        return [dict(league) for league in leagues]
    finally:
        await conn.close()

async def create_league(league: LeagueCreate):
    conn = await get_db_connection()
    settings = json.dumps(league.settings)

    try:
        league_id = await conn.fetchval("""
            INSERT INTO leagues (league_name, description, rules, settings)
            VALUES ($1, $2, $3, $4) RETURNING league_id
        """, league.league_name, league.description, league.rules, settings)
        return league_id
    finally:
        await conn.close()