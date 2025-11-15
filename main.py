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

@app.on_event("startup")
async def startup_event():
    await init_db()  # Create tables
    await seed_data()  # Seed initial data

@app.get("/")
async def root():
    return {"message": "Welcome to Crimax Sports League Management Platform"}