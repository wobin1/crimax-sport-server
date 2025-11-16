# filepath: /Applications/wobin/crimax/crimax_sport/crimax_sport_server/src/modules/seasons/router.py
from fastapi import APIRouter, HTTPException
from modules.shared.response import success_response, error_response
from typing import List
from . import manager

router = APIRouter(prefix="", tags=["seasons"])

@router.get("")
async def get_seasons():
    """Get all seasons with league information"""
    seasons = await manager.get_seasons()
    return success_response(data=seasons)

@router.get("/{season_id}")
async def get_season_by_id(season_id: int):
    """Get a specific season by ID"""
    season = await manager.get_season_by_id(season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return success_response(data=season)

@router.post("")
async def create_season(season_data: dict):
    """Create a new season"""
    season_id = await manager.create_season(season_data)
    return success_response(data=season_id, status_code=201)

@router.put("/{season_id}")
async def update_season(season_id: int, season_data: dict):
    """Update an existing season"""
    success = await manager.update_season(season_id, season_data)
    if not success:
        raise HTTPException(status_code=404, detail="Season not found")
    return success_response(data=success)

@router.delete("/{season_id}")
async def delete_season(season_id: int):
    """Delete a season"""
    success = await manager.delete_season(season_id)
    if not success:
        raise HTTPException(status_code=404, detail="Season not found")
    return success_response(data=success)
