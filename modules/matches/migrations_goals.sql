-- Create match_goals table
CREATE TABLE IF NOT EXISTS match_goals (
    id SERIAL PRIMARY KEY,
    match_id INT NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    player_id INT NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    team_id INT NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    minute INT NOT NULL,
    goal_type VARCHAR(50) DEFAULT 'regular',
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT check_minute CHECK (minute >= 0 AND minute <= 120)
);

CREATE INDEX IF NOT EXISTS idx_match_goals_match_id ON match_goals(match_id);
CREATE INDEX IF NOT EXISTS idx_match_goals_player_id ON match_goals(player_id);
