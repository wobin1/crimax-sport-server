import asyncio
import asyncpg
from pathlib import Path

async def run_migration():
    """Run the match statistics migration"""
    # Update with your database credentials
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='your_user',
        password='your_password',
        database='your_database'
    )
    
    try:
        # Read the migration file
        migration_file = Path(__file__).parent / 'migrations_statistics.sql'
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Execute the migration
        await conn.execute(sql)
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
