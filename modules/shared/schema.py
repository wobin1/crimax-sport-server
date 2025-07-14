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
    results JSONB
);

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
"""