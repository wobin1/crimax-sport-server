import bcrypt
from modules.shared.db import get_db_connection

async def seed_data():
    conn = await get_db_connection()
    try:
        # Seed users only - 4 users (balanced for different roles)
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

    finally:
        await conn.close()