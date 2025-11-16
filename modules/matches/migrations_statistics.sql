-- Add columns to matches table for scores and status if they don't exist
ALTER TABLE IF EXISTS matches 
ADD COLUMN IF NOT EXISTS home_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS away_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'scheduled';

-- Create match_statistics table
CREATE TABLE IF NOT EXISTS match_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    home_team_stats JSONB NOT NULL DEFAULT '{}',
    away_team_stats JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(match_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_match_statistics_match_id ON match_statistics(match_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);