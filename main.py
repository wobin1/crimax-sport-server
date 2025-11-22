from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.shared.db import init_db
from modules.shared.seeda import seed_data
from modules.auth.router import router as auth_router
from modules.leagues.router import router as leagues_router
from modules.teams.router import router as teams_router
from modules.players.router import router as players_router
from modules.matches.router import router as matches_router
from modules.standings.router import router as standings_router
from modules.venues.router import router as venues_router
from modules.news.router import router as news_router
from modules.seasons import router as seasons_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include all module routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(leagues_router, prefix="/leagues", tags=["leagues"])
app.include_router(teams_router, prefix="/teams", tags=["teams"])
app.include_router(players_router, prefix="/players", tags=["players"])
app.include_router(matches_router, prefix="/matches", tags=["matches"])
app.include_router(standings_router, prefix="/standings", tags=["standings"])
app.include_router(venues_router, prefix="/venues", tags=["venues"])
app.include_router(news_router, prefix="/news", tags=["news"])
app.include_router(seasons_router.router, prefix="/seasons")

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    logger.info("🚀 Starting Crimax Sport application...")
    
    try:
        # Step 1: Initialize database (create tables + run migrations)
        logger.info("📊 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized successfully")
        
        # Step 2: Seed initial data
        logger.info("🌱 Seeding initial data...")
        await seed_data()
        logger.info("✅ Data seeded successfully")
        
        logger.info("🎉 Application startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "Welcome to Crimax Sports League Management Platform"}