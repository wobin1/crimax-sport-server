from modules.shared.db import get_db_connection
from .models import PlayerCreate, PlayerUpdate
import json

async def get_players():
    conn = await get_db_connection()
    try:
        players = await conn.fetch("SELECT * FROM players")
        return [dict(player) for player in players]
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