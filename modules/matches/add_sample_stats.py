import sys
import os
from pathlib import Path
import asyncio
import requests

# Sample match statistics
sample_stats = {
    "home_stats": {
        "possession": 55,
        "shots": 12,
        "shots_on_target": 5,
        "corners": 6,
        "fouls": 10,
        "yellow_cards": 2,
        "red_cards": 0,
        "passes": 450,
        "pass_accuracy": 82
    },
    "away_stats": {
        "possession": 45,
        "shots": 8,
        "shots_on_target": 3,
        "corners": 4,
        "fouls": 12,
        "yellow_cards": 3,
        "red_cards": 0,
        "passes": 380,
        "pass_accuracy": 78
    }
}

def generate_sql(match_id: int):
    """Generate SQL INSERT statement for match statistics"""
    home_stats_json = str(sample_stats["home_stats"]).replace("'", '"')
    away_stats_json = str(sample_stats["away_stats"]).replace("'", '"')
    
    sql = f"""
-- Insert sample statistics for match {match_id}
INSERT INTO match_statistics (match_id, home_team_stats, away_team_stats, created_at, updated_at)
VALUES (
    {match_id},
    '{home_stats_json}'::jsonb,
    '{away_stats_json}'::jsonb,
    NOW(),
    NOW()
)
ON CONFLICT (match_id) 
DO UPDATE SET 
    home_team_stats = EXCLUDED.home_team_stats,
    away_team_stats = EXCLUDED.away_team_stats,
    updated_at = NOW();
"""
    return sql

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_sample_stats.py <match_id>")
        print("Example: python add_sample_stats.py 340")
        print("\nGenerating SQL for all matches:")
        print("\nOr specify a match_id to generate SQL for that specific match")
        sys.exit(1)
    
    match_id = int(sys.argv[1])
    sql = generate_sql(match_id)
    print(sql)
    print("\nCopy the above SQL and run it in your database client (e.g., pgAdmin, psql)")

