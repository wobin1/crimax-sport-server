from fastapi import APIRouter, Depends, HTTPException
from .manager import get_leagues, get_league_by_id, create_league, update_league, delete_league
from .models import LeagueCreate, LeagueUpdate
from modules.shared.response import success_response
from modules.auth.router import get_current_user

router = APIRouter()

@router.get("/")
async def list_leagues():
    leagues = await get_leagues()
    return success_response(leagues)

@router.get("/{league_id}")
async def get_league(league_id: int):
    league = await get_league_by_id(league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return success_response(league)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_league(league: LeagueCreate):
    league_id = await create_league(league)
    return success_response({"league_id": league_id})

@router.put("/{league_id}", dependencies=[Depends(get_current_user)])
async def edit_league(league_id: int, league: LeagueUpdate):
    success = await update_league(league_id, league)
    if not success:
        raise HTTPException(status_code=404, detail="League not found")
    updated_league = await get_league_by_id(league_id)
    return success_response(updated_league)

@router.delete("/{league_id}", dependencies=[Depends(get_current_user)])
async def remove_league(league_id: int):
    success = await delete_league(league_id)
    if not success:
        raise HTTPException(status_code=404, detail="League not found")
    return success_response({"message": "League deleted successfully"})