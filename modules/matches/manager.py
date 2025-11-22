from modules.shared.db import get_db_connection
from .models import MatchCreate, MatchUpdate, MatchStatistics, UpdateMatchScore
import json

async def get_matches(season_id: int = None):
    conn = await get_db_connection()
    try:
        # Build query with optional season filter, including goal counts
        query = """
            SELECT 
                m.match_id,
                m.season_id,
                m.team1_id,
                t1.team_name as team1_name,
                m.team2_id,
                t2.team_name as team2_name,
                m.venue_id,
                v.venue_name,
                m.date,
                m.time,
                m.results,
                s.season_name,
                l.league_name,
                COALESCE(
                    (SELECT COUNT(*) FROM match_goals WHERE match_id = m.match_id AND team_id = m.team1_id),
                    0
                ) as home_goals,
                COALESCE(
                    (SELECT COUNT(*) FROM match_goals WHERE match_id = m.match_id AND team_id = m.team2_id),
                    0
                ) as away_goals
            FROM matches m
            LEFT JOIN teams t1 ON m.team1_id = t1.team_id
            LEFT JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
            LEFT JOIN seasons s ON m.season_id = s.season_id
            LEFT JOIN leagues l ON s.league_id = l.league_id
        """
        
        # Add WHERE clause if season_id is provided
        if season_id is not None:
            query += " WHERE m.season_id = $1"
            matches = await conn.fetch(query, season_id)
        else:
            matches = await conn.fetch(query)
            
        return [
            {
                "match_id": match["match_id"],
                "season_id": match["season_id"],
                "season_name": match["season_name"],
                "league_name": match["league_name"],
                "team1_id": match["team1_id"],
                "team1_name": match["team1_name"],
                "team2_id": match["team2_id"],
                "team2_name": match["team2_name"],
                "venue_id": match["venue_id"],
                "venue_name": match["venue_name"],
                "date": match["date"].isoformat() if match["date"] else None,
                "time": match["time"].isoformat() if match["time"] else None,
                "results": (results := json.loads(match["results"]) if match["results"] else None),
                "home_score": match["home_goals"],  # Calculated from match_goals table
                "away_score": match["away_goals"],  # Calculated from match_goals table
                "status": results.get("status") if results else None
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
                v.venue_name,
                m.date,
                m.time,
                m.results,
                s.season_name,
                l.league_name,
                COALESCE(
                    (SELECT COUNT(*) FROM match_goals WHERE match_id = m.match_id AND team_id = m.team1_id),
                    0
                ) as home_goals,
                COALESCE(
                    (SELECT COUNT(*) FROM match_goals WHERE match_id = m.match_id AND team_id = m.team2_id),
                    0
                ) as away_goals
            FROM matches m
            LEFT JOIN teams t1 ON m.team1_id = t1.team_id
            LEFT JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
            LEFT JOIN seasons s ON m.season_id = s.season_id
            LEFT JOIN leagues l ON s.league_id = l.league_id
            WHERE m.match_id = $1
        """, match_id)

        if match:
            results = json.loads(match["results"]) if match["results"] else None
            return {
                "match_id": match["match_id"],
                "season_id": match["season_id"],
                "season_name": match["season_name"],
                "league_name": match["league_name"],
                "team1_id": match["team1_id"],
                "team1_name": match["team1_name"],
                "team2_id": match["team2_id"],
                "team2_name": match["team2_name"],
                "venue_id": match["venue_id"],
                "venue_name": match["venue_name"],
                "date": match["date"].isoformat() if match["date"] else None,
                "time": match["time"].isoformat() if match["time"] else None,
                "results": results,
                "home_score": match["home_goals"],  # Calculated from match_goals table
                "away_score": match["away_goals"],  # Calculated from match_goals table
                "status": results.get("status") if results else None
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

class MatchManager:
    def __init__(self, db):
        self.db = db

    async def get_match_by_id(self, match_id: int):
        """Get match by ID"""
        query = """
            SELECT 
                m.match_id,
                m.season_id,
                m.team1_id,
                t1.team_name as team1_name,
                m.team2_id,
                t2.team_name as team2_name,
                m.venue_id,
                v.venue_name,
                m.date,
                m.time,
                m.results,
                s.season_name,
                l.league_name
            FROM matches m
            LEFT JOIN teams t1 ON m.team1_id = t1.team_id
            LEFT JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
            LEFT JOIN seasons s ON m.season_id = s.season_id
            LEFT JOIN leagues l ON s.league_id = l.league_id
            WHERE m.match_id = $1
        """
        result = await self.db.fetchrow(query, match_id)
        if not result:
            return None
        return dict(result)

    async def update_match_score(self, match_id: str, score_update: UpdateMatchScore):
        """Update match score and status"""
        query = """
            UPDATE matches 
            SET home_score = $1, away_score = $2, status = COALESCE($3, status), updated_at = NOW()
            WHERE id = $4
            RETURNING *
        """
        result = await self.db.fetchrow(
            query, 
            score_update.home_score, 
            score_update.away_score, 
            score_update.status,
            match_id
        )
        if not result:
            return None
        return dict(result)
    
    async def create_or_update_match_statistics(self, match_id: int, statistics: MatchStatistics):
        """Create or update match statistics"""
        # Check if statistics already exist
        check_query = "SELECT id FROM match_statistics WHERE match_id = $1"
        existing = await self.db.fetchrow(check_query, match_id)
        
        if existing:
            # Update existing statistics
            query = """
                UPDATE match_statistics 
                SET home_team_stats = $1, away_team_stats = $2, updated_at = NOW()
                WHERE match_id = $3
                RETURNING *
            """
        else:
            # Insert new statistics
            query = """
                INSERT INTO match_statistics (match_id, home_team_stats, away_team_stats, updated_at)
                VALUES ($3, $1, $2, NOW())
                RETURNING *
            """
        
        result = await self.db.fetchrow(
            query,
            statistics.home_team_stats.model_dump_json(),
            statistics.away_team_stats.model_dump_json(),
            match_id
        )
        return dict(result) if result else None
    
    async def get_match_statistics(self, match_id: int):
        """Get match statistics by match ID"""
        query = """
            SELECT * FROM match_statistics WHERE match_id = $1
        """
        result = await self.db.fetchrow(query, match_id)
        if not result:
            return None
        return dict(result)