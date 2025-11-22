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
                    p.first_name,
                    p.last_name,
                    CONCAT(p.first_name, ' ', p.last_name) as player_name,
                    p.team_id,
                    t.team_name,
                    p.photo,
                    p.statistics
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
                    p.first_name,
                    p.last_name,
                    CONCAT(p.first_name, ' ', p.last_name) as player_name,
                    p.team_id,
                    t.team_name,
                    p.photo,
                    p.statistics
                FROM players p
                LEFT JOIN teams t ON p.team_id = t.team_id
                ORDER BY CONCAT(p.first_name, ' ', p.last_name)
            """
            players = await conn.fetch(query)
        
        return [
            {
                "player_id": player["player_id"],
                "first_name": player["first_name"],
                "last_name": player["last_name"],
                "player_name": player["player_name"],
                "team_id": player["team_id"],
                "team_name": player["team_name"],
                "photo": player["photo"],
                "statistics": json.loads(player["statistics"]) if player["statistics"] else None
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

async def get_top_scorers(season_id: Optional[int] = None, limit: int = 10):
    """Get top scorers based on goals from match_goals table"""
    conn = await get_db_connection()
    try:
        if season_id is not None:
            query = """
                SELECT 
                    p.player_id,
                    p.first_name,
                    p.last_name,
                    CONCAT(p.first_name, ' ', p.last_name) as player_name,
                    p.photo,
                    t.team_id,
                    t.team_name,
                    t.logo as team_logo,
                    COUNT(mg.id) as goals
                FROM players p
                LEFT JOIN teams t ON p.team_id = t.team_id
                LEFT JOIN match_goals mg ON p.player_id = mg.player_id
                LEFT JOIN matches m ON mg.match_id = m.match_id
                WHERE m.season_id = $1
                GROUP BY p.player_id, p.first_name, p.last_name, p.photo, t.team_id, t.team_name, t.logo
                HAVING COUNT(mg.id) > 0
                ORDER BY goals DESC, player_name ASC
                LIMIT $2
            """
            scorers = await conn.fetch(query, season_id, limit)
        else:
            query = """
                SELECT 
                    p.player_id,
                    p.first_name,
                    p.last_name,
                    CONCAT(p.first_name, ' ', p.last_name) as player_name,
                    p.photo,
                    t.team_id,
                    t.team_name,
                    t.logo as team_logo,
                    COUNT(mg.id) as goals
                FROM players p
                LEFT JOIN teams t ON p.team_id = t.team_id
                LEFT JOIN match_goals mg ON p.player_id = mg.player_id
                GROUP BY p.player_id, p.first_name, p.last_name, p.photo, t.team_id, t.team_name, t.logo
                HAVING COUNT(mg.id) > 0
                ORDER BY goals DESC, player_name ASC
                LIMIT $1
            """
            scorers = await conn.fetch(query, limit)
        
        return [
            {
                "player_id": scorer["player_id"],
                "first_name": scorer["first_name"],
                "last_name": scorer["last_name"],
                "player_name": scorer["player_name"],
                "photo": scorer["photo"],
                "team_id": scorer["team_id"],
                "team_name": scorer["team_name"],
                "team_logo": scorer["team_logo"],
                "goals": scorer["goals"]
            }
            for scorer in scorers
        ]
    finally:
        await conn.close()

async def get_clean_sheets(season_id: Optional[int] = None, limit: int = 10):
    """Get goalkeepers with most clean sheets (matches where their team didn't concede)"""
    conn = await get_db_connection()
    try:
        if season_id is not None:
            query = """
                WITH goalkeeper_matches AS (
                    SELECT DISTINCT
                        p.player_id,
                        p.first_name,
                        p.last_name,
                        CONCAT(p.first_name, ' ', p.last_name) as player_name,
                        p.photo,
                        t.team_id,
                        t.team_name,
                        t.logo as team_logo,
                        m.match_id,
                        CASE 
                            WHEN m.team1_id = t.team_id THEN m.team2_id
                            WHEN m.team2_id = t.team_id THEN m.team1_id
                        END as opponent_team_id
                    FROM players p
                    JOIN teams t ON p.team_id = t.team_id
                    JOIN matches m ON (m.team1_id = t.team_id OR m.team2_id = t.team_id)
                    WHERE m.season_id = $1
                        AND p.statistics::jsonb->>'position' = 'Goalkeeper'
                ),
                clean_sheet_counts AS (
                    SELECT 
                        gm.player_id,
                        gm.first_name,
                        gm.last_name,
                        gm.player_name,
                        gm.photo,
                        gm.team_id,
                        gm.team_name,
                        gm.team_logo,
                        COUNT(DISTINCT gm.match_id) as total_matches,
                        COUNT(DISTINCT CASE 
                            WHEN NOT EXISTS (
                                SELECT 1 FROM match_goals mg 
                                WHERE mg.match_id = gm.match_id 
                                AND mg.team_id = gm.opponent_team_id
                            ) THEN gm.match_id 
                        END) as clean_sheets
                    FROM goalkeeper_matches gm
                    GROUP BY gm.player_id, gm.first_name, gm.last_name, gm.player_name, 
                             gm.photo, gm.team_id, gm.team_name, gm.team_logo
                )
                SELECT * FROM clean_sheet_counts
                WHERE clean_sheets > 0
                ORDER BY clean_sheets DESC, player_name ASC
                LIMIT $2
            """
            keepers = await conn.fetch(query, season_id, limit)
        else:
            query = """
                WITH goalkeeper_matches AS (
                    SELECT DISTINCT
                        p.player_id,
                        p.first_name,
                        p.last_name,
                        CONCAT(p.first_name, ' ', p.last_name) as player_name,
                        p.photo,
                        t.team_id,
                        t.team_name,
                        t.logo as team_logo,
                        m.match_id,
                        CASE 
                            WHEN m.team1_id = t.team_id THEN m.team2_id
                            WHEN m.team2_id = t.team_id THEN m.team1_id
                        END as opponent_team_id
                    FROM players p
                    JOIN teams t ON p.team_id = t.team_id
                    JOIN matches m ON (m.team1_id = t.team_id OR m.team2_id = t.team_id)
                    WHERE p.statistics::jsonb->>'position' = 'Goalkeeper'
                ),
                clean_sheet_counts AS (
                    SELECT 
                        gm.player_id,
                        gm.first_name,
                        gm.last_name,
                        gm.player_name,
                        gm.photo,
                        gm.team_id,
                        gm.team_name,
                        gm.team_logo,
                        COUNT(DISTINCT gm.match_id) as total_matches,
                        COUNT(DISTINCT CASE 
                            WHEN NOT EXISTS (
                                SELECT 1 FROM match_goals mg 
                                WHERE mg.match_id = gm.match_id 
                                AND mg.team_id = gm.opponent_team_id
                            ) THEN gm.match_id 
                        END) as clean_sheets
                    FROM goalkeeper_matches gm
                    GROUP BY gm.player_id, gm.first_name, gm.last_name, gm.player_name, 
                             gm.photo, gm.team_id, gm.team_name, gm.team_logo
                )
                SELECT * FROM clean_sheet_counts
                WHERE clean_sheets > 0
                ORDER BY clean_sheets DESC, player_name ASC
                LIMIT $1
            """
            keepers = await conn.fetch(query, limit)
        
        return [
            {
                "player_id": keeper["player_id"],
                "first_name": keeper["first_name"],
                "last_name": keeper["last_name"],
                "player_name": keeper["player_name"],
                "photo": keeper["photo"],
                "team_id": keeper["team_id"],
                "team_name": keeper["team_name"],
                "team_logo": keeper["team_logo"],
                "clean_sheets": keeper["clean_sheets"],
                "total_matches": keeper["total_matches"]
            }
            for keeper in keepers
        ]
    finally:
        await conn.close()