from modules.shared.db import get_db_connection
from .models import MatchCreate, MatchUpdate, MatchStatistics, UpdateMatchScore
import json
from typing import Optional

async def get_matches(season_id: Optional[int] = None):
    conn = await get_db_connection()
    try:
        query = """
            SELECT 
                m.match_id,
                m.season_id,
                m.team1_id,
                t1.team_name as team1_name,
                m.team2_id,
                t2.team_name as team2_name,
                m.venue_id,
                v.venue_name as venue_name,
                m.date,
                m.time,
                m.results
            FROM matches m
            LEFT JOIN teams t1 ON m.team1_id = t1.team_id
            LEFT JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
        """
        
        params = []
        if season_id is not None:
            query += " WHERE m.season_id = $1"
            params.append(season_id)
            
        query += " ORDER BY m.date DESC, m.time DESC"
        
        if params:
            matches = await conn.fetch(query, *params)
        else:
            matches = await conn.fetch(query)
            
        return [
            {
                "match_id": match["match_id"],
                "season_id": match["season_id"],
                "team1_id": match["team1_id"],
                "team1_name": match["team1_name"],
                "team2_id": match["team2_id"],
                "team2_name": match["team2_name"],
                "venue_id": match["venue_id"],
                "venue_name": match["venue_name"],
                "date": match["date"].isoformat() if match["date"] else None,
                "time": match["time"].isoformat() if match["time"] else None,
                "results": json.loads(match["results"]) if match["results"] else None
            }
            for match in matches
        ]
    finally:
        await conn.close()

async def get_match_by_id(match_id: int):
    conn = await get_db_connection()
    try:
        match = await conn.fetchrow("""
            SELECT 
                m.match_id,
                m.season_id,
                m.team1_id,
                t1.team_name as team1_name,
                m.team2_id,
                t2.team_name as team2_name,
                m.venue_id,
                v.venue_name as venue_name,
                m.date,
                m.time,
                m.results,
                m.home_score,
                m.away_score,
                m.status
            FROM matches m
            LEFT JOIN teams t1 ON m.team1_id = t1.team_id
            LEFT JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
            WHERE m.match_id = $1
        """, match_id)

        if match:
            return {
                "match_id": match["match_id"],
                "season_id": match["season_id"],
                "team1_id": match["team1_id"],
                "team1_name": match["team1_name"],
                "team2_id": match["team2_id"],
                "team2_name": match["team2_name"],
                "venue_id": match["venue_id"],
                "venue_name": match["venue_name"],
                "date": match["date"].isoformat() if match["date"] else None,
                "time": match["time"].isoformat() if match["time"] else None,
                "results": json.loads(match["results"]) if match["results"] else None,
                "home_score": match["home_score"],
                "away_score": match["away_score"],
                "status": match["status"]
            }
        else:
            return None
    finally:
        await conn.close()

async def create_match(match: MatchCreate):
    conn = await get_db_connection()
    match_results = json.dumps(match.results)
    try:
        match_id = await conn.fetchval("""
            INSERT INTO matches (season_id, team1_id, team2_id, venue_id, date, time, results)
            VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING match_id
        """, match.season_id, match.team1_id, match.team2_id, match.venue_id, match.date, match.time, match_results)
        return match_id
    finally:
        await conn.close()

async def update_match(match_id: int, match: MatchUpdate):
    conn = await get_db_connection()
    match_results = json.dumps(match.results)
    try:
        result = await conn.execute("""
            UPDATE matches 
            SET season_id = COALESCE($2, season_id),
                team1_id = COALESCE($3, team1_id),
                team2_id = COALESCE($4, team2_id),
                venue_id = COALESCE($5, venue_id),
                date = COALESCE($6, date),
                time = COALESCE($7, time),
                results = COALESCE($8, results)
            WHERE match_id = $1
        """, match_id, match.season_id, match.team1_id, match.team2_id, match.venue_id, match.date, match.time, match_results)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_match(match_id: int):
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM matches WHERE match_id = $1", match_id)
        return result == "DELETE 1"
    finally:
        await conn.close()

async def get_match_statistics(match_id: int):
    """Get match statistics by match ID"""
    conn = await get_db_connection()
    try:
        result = await conn.fetchrow("""
            SELECT * FROM match_statistics WHERE match_id = $1
        """, match_id)
        if not result:
            return None
        return dict(result)
    finally:
        await conn.close()

async def create_or_update_match_statistics(match_id: int, home_stats: dict, away_stats: dict):
    """Create or update match statistics"""
    conn = await get_db_connection()
    try:
        # Check if statistics already exist
        existing = await conn.fetchrow("""
            SELECT id FROM match_statistics WHERE match_id = $1
        """, match_id)
        
        if existing:
            # Update existing statistics
            result = await conn.fetchrow("""
                UPDATE match_statistics 
                SET home_team_stats = $1, away_team_stats = $2, updated_at = NOW()
                WHERE match_id = $3
                RETURNING *
            """, json.dumps(home_stats), json.dumps(away_stats), match_id)
        else:
            # Insert new statistics
            result = await conn.fetchrow("""
                INSERT INTO match_statistics (match_id, home_team_stats, away_team_stats, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                RETURNING *
            """, match_id, json.dumps(home_stats), json.dumps(away_stats))
        
        return dict(result) if result else None
    finally:
        await conn.close()

async def update_match_score(match_id: int, home_score: int, away_score: int):
    """Update match scores"""
    conn = await get_db_connection()
    try:
        result = await conn.execute("""
            UPDATE matches 
            SET home_score = $1, away_score = $2, status = 'completed'
            WHERE match_id = $3
        """, home_score, away_score, match_id)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def add_match_goal(match_id: int, player_id: int, team_id: int, minute: int, goal_type: str = 'regular'):
    """Add a goal to a match"""
    conn = await get_db_connection()
    try:
        goal_id = await conn.fetchval("""
            INSERT INTO match_goals (match_id, player_id, team_id, minute, goal_type, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            RETURNING id
        """, match_id, player_id, team_id, minute, goal_type)
        
        # Update match scores
        home_score = await conn.fetchval("""
            SELECT COUNT(*) FROM match_goals mg
            JOIN matches m ON mg.match_id = m.match_id
            WHERE mg.match_id = $1 AND mg.team_id = m.team1_id
        """, match_id)
        
        away_score = await conn.fetchval("""
            SELECT COUNT(*) FROM match_goals mg
            JOIN matches m ON mg.match_id = m.match_id
            WHERE mg.match_id = $1 AND mg.team_id = m.team2_id
        """, match_id)
        
        await conn.execute("""
            UPDATE matches 
            SET home_score = $1, away_score = $2
            WHERE match_id = $3
        """, home_score, away_score, match_id)
        
        return goal_id
    finally:
        await conn.close()

async def get_match_goals(match_id: int):
    """Get all goals for a match"""
    conn = await get_db_connection()
    try:
        goals = await conn.fetch("""
            SELECT 
                mg.id,
                mg.match_id,
                mg.player_id,
                CONCAT(p.first_name, ' ', p.last_name) as player_name,
                mg.team_id,
                t.team_name,
                mg.minute,
                mg.goal_type,
                mg.created_at
            FROM match_goals mg
            JOIN players p ON mg.player_id = p.player_id
            JOIN teams t ON mg.team_id = t.team_id
            WHERE mg.match_id = $1
            ORDER BY mg.minute ASC
        """, match_id)
        
        return [dict(goal) for goal in goals]
    finally:
        await conn.close()

async def delete_match_goal(goal_id: int):
    """Delete a goal from a match"""
    conn = await get_db_connection()
    try:
        # Get match_id before deleting
        match_id = await conn.fetchval("""
            SELECT match_id FROM match_goals WHERE id = $1
        """, goal_id)
        
        if not match_id:
            return False
        
        result = await conn.execute("DELETE FROM match_goals WHERE id = $1", goal_id)
        
        # Update match scores
        home_score = await conn.fetchval("""
            SELECT COUNT(*) FROM match_goals mg
            JOIN matches m ON mg.match_id = m.match_id
            WHERE mg.match_id = $1 AND mg.team_id = m.team1_id
        """, match_id)
        
        away_score = await conn.fetchval("""
            SELECT COUNT(*) FROM match_goals mg
            JOIN matches m ON mg.match_id = m.match_id
            WHERE mg.match_id = $1 AND mg.team_id = m.team2_id
        """, match_id)
        
        await conn.execute("""
            UPDATE matches 
            SET home_score = $1, away_score = $2
            WHERE match_id = $3
        """, home_score, away_score, match_id)
        
        return result == "DELETE 1"
    finally:
        await conn.close()