from fastapi import APIRouter, Depends, HTTPException
from .manager import get_matches, get_match_by_id, create_match, update_match, delete_match, get_match_statistics, create_or_update_match_statistics, add_match_goal, get_match_goals, delete_match_goal
from .models import MatchCreate, MatchUpdate
from modules.shared.response import success_response, error_response
from modules.auth.router import get_current_user
import json
from typing import Optional

router = APIRouter()

@router.get("/")
async def list_matches(season_id: Optional[int] = None):
    """Get all matches, optionally filtered by season_id"""
    matches = await get_matches(season_id=season_id)
    return success_response(matches)

@router.get("/{match_id}")
async def get_match(match_id: int):
    match = await get_match_by_id(match_id)
    if not match:
        return error_response("Match not found", 404)
    return success_response(match)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_match(match: MatchCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    match_id = await create_match(match)
    return success_response({"match_id": match_id}, 201)

@router.put("/{match_id}", dependencies=[Depends(get_current_user)])
async def edit_match(match_id: int, match: MatchUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    updated = await update_match(match_id, match)
    if not updated:
        return error_response("Match not found", 404)
    return success_response({"message": "Match updated"})

@router.delete("/{match_id}", dependencies=[Depends(get_current_user)])
async def remove_match(match_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    deleted = await delete_match(match_id)
    if not deleted:
        return error_response("Match not found", 404)
    return success_response({"message": "Match deleted"})

@router.get("/{match_id}/stats")
async def get_match_stats(match_id: int):
    """Get match statistics by match ID"""
    stats = await get_match_statistics(match_id)
    if not stats:
        return success_response(None)
    return success_response(stats)

@router.post("/{match_id}/stats")
async def create_match_stats(match_id: int, home_stats: dict, away_stats: dict):
    """Create or update match statistics"""
    # Verify match exists
    match = await get_match_by_id(match_id)
    if not match:
        return error_response("Match not found", 404)
    
    stats = await create_or_update_match_statistics(match_id, home_stats, away_stats)
    if not stats:
        return error_response("Failed to create statistics", 500)
    return success_response(stats)

@router.put("/{match_id}/score")
async def update_match_score(match_id: int, home_score: int, away_score: int):
    """Update match scores"""
    from .manager import update_match_score
    
    # Verify match exists
    match = await get_match_by_id(match_id)
    if not match:
        return error_response("Match not found", 404)
    
    success = await update_match_score(match_id, home_score, away_score)
    if not success:
        return error_response("Failed to update scores", 500)
    return success_response({"message": "Scores updated successfully"})

@router.post("/{match_id}/goals")
async def add_goal(match_id: int, player_id: int, team_id: int, minute: int, goal_type: str = 'regular'):
    """Add a goal to a match"""
    # Verify match exists
    match = await get_match_by_id(match_id)
    if not match:
        return error_response("Match not found", 404)
    
    goal_id = await add_match_goal(match_id, player_id, team_id, minute, goal_type)
    if not goal_id:
        return error_response("Failed to add goal", 500)
    return success_response({"goal_id": goal_id, "message": "Goal added successfully"})

@router.get("/{match_id}/goals")
async def get_goals(match_id: int):
    """Get all goals for a match"""
    goals = await get_match_goals(match_id)
    return success_response(goals)

@router.delete("/goals/{goal_id}")
async def delete_goal(goal_id: int):
    """Delete a goal"""
    success = await delete_match_goal(goal_id)
    if not success:
        return error_response("Goal not found", 404)
    return success_response({"message": "Goal deleted successfully"})