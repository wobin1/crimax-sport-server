from modules.shared.db import get_db_connection
from .models import MatchCreate, MatchUpdate
import json

async def get_matches():
    conn = await get_db_connection()
    try:
        matches = await conn.fetch("SELECT * FROM matches")
        return [
            {
                "match_id": match["match_id"],
                "season_id": match["season_id"],
                "team1_id": match["team1_id"],
                "team2_id": match["team2_id"],
                "venue_id": match["venue_id"],
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
        match = await conn.fetchrow("SELECT * FROM matches WHERE match_id = $1", match_id)

        if match:
            return [
                {
                    "match_id": match["match_id"],
                    "season_id": match["season_id"],
                    "team1_id": match["team1_id"],
                    "team2_id": match["team2_id"],
                    "venue_id": match["venue_id"],
                    "date": match["date"].isoformat() if match["date"] else None,
                    "time": match["time"].isoformat() if match["time"] else None,
                    "results": json.loads(match["results"]) if match["results"] else None
                }
            ]
        else:
            return match
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