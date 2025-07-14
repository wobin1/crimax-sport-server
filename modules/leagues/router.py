from fastapi import APIRouter, Depends
from .manager import get_leagues, create_league
from .models import LeagueCreate
from modules.shared.response import success_response
from modules.auth.router import get_current_user

router = APIRouter()

@router.get("/")
async def list_leagues():
    leagues = await get_leagues()
    return success_response(leagues)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_league(league: LeagueCreate):
    league_id = await create_league(league)
    return success_response({"league_id": league_id})