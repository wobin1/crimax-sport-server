import bcrypt
from modules.shared.db import get_db_connection

async def seed_data():
    conn = await get_db_connection()
    try:
        # Seed users (admin, team manager, player, guest)
        admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await conn.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES 
                ('admin', 'admin@crimax.com', $1, 'admin'),
                ('manager1', 'manager1@crimax.com', $1, 'team_manager'),
                ('player1', 'player1@crimax.com', $1, 'player'),
                ('fan1', 'fan1@crimax.com', $1, 'guest')
            ON CONFLICT (username) DO NOTHING;
        """, admin_password)

        # Seed leagues
        await conn.execute("""
            INSERT INTO leagues (league_name, description, rules, settings)
            VALUES 
                ('Crimax Premier League', 'Top-tier league', 'Standard rules', '{"max_teams": 8}'),
                ('Crimax Amateur League', 'Entry-level league', 'Simplified rules', '{"max_teams": 6}')
            ON CONFLICT (league_name) DO NOTHING;
        """)

        # Seed seasons
        await conn.execute("""
            INSERT INTO seasons (league_id, season_name, start_date, end_date)
            VALUES 
                (1, 'Spring 2025', '2025-03-01', '2025-06-30'),
                (2, 'Winter 2025', '2025-01-01', '2025-04-30')
            ON CONFLICT DO NOTHING;
        """)

        # Seed divisions
        await conn.execute("""
            INSERT INTO divisions (league_id, division_name)
            VALUES 
                (1, 'Division A'),
                (1, 'Division B'),
                (2, 'Division C')
            ON CONFLICT DO NOTHING;
        """)

        # Seed teams
        await conn.execute("""
            INSERT INTO teams (league_id, division_id, team_name, logo, contact_info)
            VALUES 
                (1, 1, 'Thunder Bolts', '/logos/thunder.png', '{"coach": "John Doe", "phone": "123-456-7890"}'),
                (1, 1, 'Fire Strikers', '/logos/fire.png', '{"coach": "Jane Smith", "phone": "098-765-4321"}'),
                (1, 2, 'Ice Warriors', '/logos/ice.png', '{"coach": "Mike Lee", "phone": "555-555-5555"}'),
                (2, 3, 'Shadow Runners', '/logos/shadow.png', '{"coach": "Alex Brown", "phone": "444-444-4444"}')
            ON CONFLICT DO NOTHING;
        """)

        # Seed players
        await conn.execute("""
            INSERT INTO players (team_id, first_name, last_name, photo, statistics)
            VALUES 
                (1, 'Tom', 'Brady', '/photos/tom.jpg', '{"goals": 5, "assists": 3}'),
                (1, 'Serena', 'Williams', '/photos/serena.jpg', '{"goals": 2, "assists": 7}'),
                (2, 'LeBron', 'James', '/photos/lebron.jpg', '{"goals": 8, "assists": 1}'),
                (3, 'Mia', 'Hamm', '/photos/mia.jpg', '{"goals": 4, "assists": 4}')
            ON CONFLICT DO NOTHING;
        """)

        # Seed venues
        await conn.execute("""
            INSERT INTO venues (venue_name, address, capacity)
            VALUES 
                ('Crimax Arena', '123 Main St, Crimax City', 5000),
                ('Victory Field', '456 Oak Ave, Victory Town', 3000)
            ON CONFLICT DO NOTHING;
        """)

        # Seed matches
        await conn.execute("""
            INSERT INTO matches (season_id, team1_id, team2_id, venue_id, date, time, results)
            VALUES 
                (1, 1, 2, 1, '2025-03-10', '14:00:00', '{"team1_score": 3, "team2_score": 2}'),
                (1, 3, 1, 2, '2025-03-15', '16:00:00', '{"team1_score": 1, "team2_score": 1}'),
                (2, 4, 2, 1, '2025-01-20', '15:00:00', '{"team1_score": 0, "team2_score": 4}')
            ON CONFLICT DO NOTHING;
        """)

        # Seed token_blacklist (example revoked token, normally populated by logout)
        await conn.execute("""
            INSERT INTO token_blacklist (token, expires_at)
            VALUES 
                ('example.revoked.token', '2025-12-31 23:59:59')
            ON CONFLICT (token) DO NOTHING;
        """)

        # Optional: Seed announcements (if you’ve added this table)
        await conn.execute("""
            INSERT INTO announcements (league_id, user_id, title, content, timestamp)
            VALUES 
                (1, 1, 'Season Start', 'The Spring 2025 season begins March 1st!', '2025-02-15 10:00:00')
            ON CONFLICT DO NOTHING;
        """)

        # Optional: Seed messages (if you’ve added this table)
        await conn.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, timestamp)
            VALUES 
                (1, 2, 'Good luck this season!', '2025-02-20 09:00:00')
            ON CONFLICT DO NOTHING;
        """)

    finally:
        await conn.close()