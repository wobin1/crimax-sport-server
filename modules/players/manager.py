from modules.shared.db import get_db_connection
from .models import PlayerCreate, PlayerUpdate
import json
from typing import Optional

async def get_players(team_id: Optional[int] = None):
    conn = await get_db_connection()
    try:
        if team_id is not None:
            query = """
                SELECT 
                    p.player_id,
                    CONCAT(p.first_name, ' ', p.last_name) as player_name,
                    p.team_id,
                    t.team_name
                FROM players p
                LEFT JOIN teams t ON p.team_id = t.team_id
                WHERE p.team_id = $1
                ORDER BY CONCAT(p.first_name, ' ', p.last_name)
            """
            players = await conn.fetch(query, team_id)
        else:
            query = """
                SELECT 
                    p.player_id,
                    CONCAT(p.first_name, ' ', p.last_name) as player_name,
                    p.team_id,
                    t.team_name
                FROM players p
                LEFT JOIN teams t ON p.team_id = t.team_id
                ORDER BY CONCAT(p.first_name, ' ', p.last_name)
            """
            players = await conn.fetch(query)
        
        return [
            {
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "team_id": player["team_id"],
                "team_name": player["team_name"]
            }
            for player in players
        ]
    finally:
        await conn.close()

async def get_player_by_id(player_id: int):
    conn = await get_db_connection()
    try:
        player = await conn.fetchrow("SELECT * FROM players WHERE player_id = $1", player_id)
        return dict(player) if player else None
    finally:
        await conn.close()

async def create_player(player: PlayerCreate):
    conn = await get_db_connection()
    player_statistics = json.dumps(player.statistics)
    try:
        player_id = await conn.fetchval("""
            INSERT INTO players (team_id, first_name, last_name, photo, statistics)
            VALUES ($1, $2, $3, $4, $5) RETURNING player_id
        """, player.team_id, player.first_name, player.last_name, player.photo, player_statistics)
        return player_id
    finally:
        await conn.close()

async def update_player(player_id: int, player: PlayerUpdate):
    conn = await get_db_connection()
    player_statistics = json.dumps(player.statistics)
    try:
        result = await conn.execute("""
            UPDATE players 
            SET team_id = COALESCE($2, team_id),
                first_name = COALESCE($3, first_name),
                last_name = COALESCE($4, last_name),
                photo = COALESCE($5, photo),
                statistics = COALESCE($6, statistics)
            WHERE player_id = $1
        """, player_id, player.team_id, player.first_name, player.last_name, player.photo, player_statistics)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_player(player_id: int):
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM players WHERE player_id = $1", player_id)
        return result == "DELETE 1"
    finally:
        await conn.close()