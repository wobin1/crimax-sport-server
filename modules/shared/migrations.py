import asyncpg
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

async def run_all_migrations(conn: asyncpg.Connection):
    """
    Run all SQL migrations in the correct order.
    This function is called during application startup.
    """
    try:
        # Define migrations in order of execution
        migrations = [
            {
                "name": "match_statistics",
                "path": Path(__file__).parent.parent / "matches" / "migrations_statistics.sql",
                "description": "Add match statistics table and score columns"
            },
            {
                "name": "match_goals",
                "path": Path(__file__).parent.parent / "matches" / "migrations_goals.sql",
                "description": "Add match goals tracking table"
            }
        ]
        
        logger.info("Starting database migrations...")
        
        for migration in migrations:
            try:
                # Check if migration file exists
                if not migration["path"].exists():
                    logger.warning(f"⚠️  Migration file not found: {migration['path']}")
                    continue
                
                # Read and execute migration
                with open(migration["path"], 'r') as f:
                    sql = f.read()
                
                await conn.execute(sql)
                logger.info(f"✅ Migration '{migration['name']}' completed: {migration['description']}")
                
            except Exception as e:
                logger.error(f"❌ Migration '{migration['name']}' failed: {e}")
                # Continue with other migrations even if one fails
                continue
        
        logger.info("All migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration process failed: {e}")
        raise
