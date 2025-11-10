from modules.shared.db import get_db_connection
from .models import LeagueCreate, LeagueUpdate
import json

async def get_leagues():
    conn = await get_db_connection()
    try:
        leagues = await conn.fetch("SELECT * FROM leagues")
        result = []
        for league in leagues:
            league_dict = dict(league)
            # Parse settings JSON string to dict
            if league_dict.get('settings'):
                try:
                    league_dict['settings'] = json.loads(league_dict['settings'])
                except (json.JSONDecodeError, TypeError):
                    league_dict['settings'] = None
            result.append(league_dict)
        return result
    finally:
        await conn.close()

async def get_league_by_id(league_id: int):
    conn = await get_db_connection()
    try:
        league = await conn.fetchrow("SELECT * FROM leagues WHERE league_id = $1", league_id)
        if league:
            league_dict = dict(league)
            # Parse settings JSON string to dict
            if league_dict.get('settings'):
                try:
                    league_dict['settings'] = json.loads(league_dict['settings'])
                except (json.JSONDecodeError, TypeError):
                    league_dict['settings'] = None
            return league_dict
        return None
    finally:
        await conn.close()

async def create_league(league: LeagueCreate):
    conn = await get_db_connection()
    settings = json.dumps(league.settings) if league.settings else None

    try:
        league_id = await conn.fetchval("""
            INSERT INTO leagues (league_name, description, rules, settings)
            VALUES ($1, $2, $3, $4) RETURNING league_id
        """, league.league_name, league.description, league.rules, settings)
        return league_id
    finally:
        await conn.close()

async def update_league(league_id: int, league: LeagueUpdate):
    conn = await get_db_connection()
    settings = json.dumps(league.settings) if league.settings else None
    try:
        result = await conn.execute("""
            UPDATE leagues 
            SET league_name = COALESCE($2, league_name),
                description = COALESCE($3, description),
                rules = COALESCE($4, rules),
                settings = COALESCE($5, settings)
            WHERE league_id = $1
        """, league_id, league.league_name, league.description, league.rules, settings)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_league(league_id: int):
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM leagues WHERE league_id = $1", league_id)
        return result == "DELETE 1"
    finally:
        await conn.close()