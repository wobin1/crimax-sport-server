from modules.shared.db import get_db_connection
from .models import TeamCreate, TeamUpdate
import json

async def get_teams():
    conn = await get_db_connection()
    try:
        teams = await conn.fetch("SELECT * FROM teams")
        return [dict(team) for team in teams]
    finally:
        await conn.close()

async def get_team_by_id(team_id: int):
    conn = await get_db_connection()
    try:
        team = await conn.fetchrow("SELECT * FROM teams WHERE team_id = $1", team_id)
        return dict(team) if team else None
    finally:
        await conn.close()

async def create_team(team: TeamCreate):
    contact_info = json.dumps(team.contact_info) if team.contact_info else None
    conn = await get_db_connection()
    try:
        team_id = await conn.fetchval("""
            INSERT INTO teams (league_id, division_id, team_name, logo, contact_info)
            VALUES ($1, $2, $3, $4, $5) RETURNING team_id
        """, team.league_id, team.division_id, team.team_name, team.logo, contact_info)
        return team_id
    finally:
        await conn.close()

async def update_team(team_id: int, team: TeamUpdate):
    conn = await get_db_connection()
    contact_info = json.dumps(team.contact_info)
    try:
        result = await conn.execute("""
            UPDATE teams 
            SET team_name = COALESCE($2, team_name),
                logo = COALESCE($3, logo),
                contact_info = COALESCE($4, contact_info),
                league_id = COALESCE($5, league_id),
                division_id = COALESCE($6, division_id)
            WHERE team_id = $1
        """, team_id, team.team_name, team.logo, contact_info, team.league_id, team.division_id)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_team(team_id: int):
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM teams WHERE team_id = $1", team_id)
        return result == "DELETE 1"
    finally:
        await conn.close()