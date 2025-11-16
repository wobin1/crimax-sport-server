CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'team_manager', 'player', 'guest'))
);

CREATE TABLE IF NOT EXISTS token_blacklist (
    token TEXT PRIMARY KEY,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS leagues (
    league_id SERIAL PRIMARY KEY,
    league_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    rules TEXT,
    settings JSONB
);

CREATE TABLE IF NOT EXISTS seasons (
    season_id SERIAL PRIMARY KEY,
    league_id INT REFERENCES leagues(league_id),
    season_name VARCHAR(50),
    start_date DATE,
    end_date DATE
);

CREATE TABLE IF NOT EXISTS divisions (
    division_id SERIAL PRIMARY KEY,
    league_id INT REFERENCES leagues(league_id),
    division_name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY,
    league_id INT REFERENCES leagues(league_id),
    division_id INT REFERENCES divisions(division_id),
    team_name VARCHAR(100) NOT NULL,
    logo VARCHAR(255),
    contact_info JSONB
);

CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    team_id INT REFERENCES teams(team_id),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    photo VARCHAR(255),
    statistics JSONB
);

CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    season_id INT REFERENCES seasons(season_id),
    team1_id INT REFERENCES teams(team_id),
    team2_id INT REFERENCES teams(team_id),
    venue_id INT,
    date DATE,
    time TIME,
    results JSONB,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'scheduled'
);

CREATE TABLE IF NOT EXISTS match_statistics (
    id SERIAL PRIMARY KEY,
    match_id INT NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    home_team_stats JSONB NOT NULL DEFAULT '{}',
    away_team_stats JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(match_id)
);

CREATE INDEX IF NOT EXISTS idx_match_statistics_match_id ON match_statistics(match_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);

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

CREATE TABLE IF NOT EXISTS venues (
    venue_id SERIAL PRIMARY KEY,
    venue_name VARCHAR(100),
    address TEXT,
    capacity INT
);

CREATE TABLE IF NOT EXISTS announcements (
    announcement_id SERIAL PRIMARY KEY,
    league_id INT REFERENCES leagues(league_id),
    user_id INT REFERENCES users(user_id),
    title VARCHAR(100),
    content TEXT,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES users(user_id),
    receiver_id INT REFERENCES users(user_id),
    content TEXT,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sections (
    section_id SERIAL PRIMARY KEY,
    section_name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS news (
    news_id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(section_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    excerpt TEXT,
    content TEXT NOT NULL,
    image VARCHAR(500),
    author_id INT REFERENCES users(user_id),
    author_name VARCHAR(100),
    author_avatar VARCHAR(500),
    read_time INT DEFAULT 5,
    tags TEXT[],
    featured BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_news_section ON news(section_id);
CREATE INDEX IF NOT EXISTS idx_news_slug ON news(slug);
CREATE INDEX IF NOT EXISTS idx_news_published ON news(is_published, published_at);
CREATE INDEX IF NOT EXISTS idx_news_featured ON news(featured);
CREATE INDEX IF NOT EXISTS idx_sections_slug ON sections(slug);
"""