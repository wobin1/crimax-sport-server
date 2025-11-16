import asyncio
import asyncpg
from pathlib import Path
import os

async def run_migration():
    # Database connection details - update these to match your setup
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "your_password_here"),  # UPDATE THIS
        database=os.getenv("DB_NAME", "crimax_sport")
    )
    
    try:
        # Read the migration file
        migration_file = Path(__file__).parent / "migrations_goals.sql"
        
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Execute the migration
        await conn.execute(sql)
        print("✅ Goals migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
