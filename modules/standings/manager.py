from modules.shared.db import get_db_connection

async def get_league_standings(league_id: int):
    conn = await get_db_connection()
    try:
        standings_query = """
            WITH match_scores AS (
                -- Calculate scores from match_goals table
                SELECT 
                    m.match_id,
                    m.team1_id,
                    m.team2_id,
                    COALESCE((SELECT COUNT(*) FROM match_goals WHERE match_id = m.match_id AND team_id = m.team1_id), 0) as team1_score,
                    COALESCE((SELECT COUNT(*) FROM match_goals WHERE match_id = m.match_id AND team_id = m.team2_id), 0) as team2_score
                FROM matches m
                JOIN seasons s ON m.season_id = s.season_id
                WHERE s.league_id = $1
                    AND m.date <= CURRENT_DATE  -- Only include matches that have occurred
            ),
            match_results AS (
                -- Home team results
                SELECT 
                    team1_id AS team_id,
                    team1_score AS score_for,
                    team2_score AS score_against,
                    CASE 
                        WHEN team1_score > team2_score THEN 3
                        WHEN team1_score = team2_score THEN 1
                        ELSE 0
                    END AS points
                FROM match_scores
                WHERE team1_score > 0 OR team2_score > 0  -- Only include matches with goals
                UNION ALL
                -- Away team results
                SELECT 
                    team2_id AS team_id,
                    team2_score AS score_for,
                    team1_score AS score_against,
                    CASE 
                        WHEN team2_score > team1_score THEN 3
                        WHEN team2_score = team1_score THEN 1
                        ELSE 0
                    END AS points
                FROM match_scores
                WHERE team1_score > 0 OR team2_score > 0  -- Only include matches with goals
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