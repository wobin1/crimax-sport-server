from modules.shared.db import get_db_connection

async def get_league_standings(league_id: int):
    conn = await get_db_connection()
    try:
        standings_query = """
            WITH match_results AS (
                SELECT 
                    m.team1_id AS team_id,
                    m.results->>'team1_score' AS score_for,
                    m.results->>'team2_score' AS score_against,
                    CASE 
                        WHEN (m.results->>'team1_score')::int > (m.results->>'team2_score')::int THEN 3
                        WHEN (m.results->>'team1_score')::int = (m.results->>'team2_score')::int THEN 1
                        ELSE 0
                    END AS points
                FROM matches m
                JOIN seasons s ON m.season_id = s.season_id
                WHERE s.league_id = $1 AND m.results IS NOT NULL
                UNION ALL
                SELECT 
                    m.team2_id AS team_id,
                    m.results->>'team2_score' AS score_for,
                    m.results->>'team1_score' AS score_against,
                    CASE 
                        WHEN (m.results->>'team2_score')::int > (m.results->>'team1_score')::int THEN 3
                        WHEN (m.results->>'team2_score')::int = (m.results->>'team1_score')::int THEN 1
                        ELSE 0
                    END AS points
                FROM matches m
                JOIN seasons s ON m.season_id = s.season_id
                WHERE s.league_id = $1 AND m.results IS NOT NULL
            )
            SELECT 
                t.team_id,
                t.team_name,
                COUNT(*) AS matches_played,
                SUM(CASE WHEN score_for::int > score_against::int THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN score_for::int = score_against::int THEN 1 ELSE 0 END) AS draws,
                SUM(CASE WHEN score_for::int < score_against::int THEN 1 ELSE 0 END) AS losses,
                SUM(score_for::int) AS goals_for,
                SUM(score_against::int) AS goals_against,
                SUM(points) AS points
            FROM match_results mr
            JOIN teams t ON mr.team_id = t.team_id
            GROUP BY t.team_id, t.team_name
            ORDER BY points DESC, (SUM(score_for::int) - SUM(score_against::int)) DESC, SUM(score_for::int) DESC;
        """
        standings = await conn.fetch(standings_query, league_id)
        return [dict(row) for row in standings] if standings else None
    finally:
        await conn.close()