from fastapi import APIRouter, Depends, HTTPException
from .manager import get_teams, get_team_by_id, create_team, update_team, delete_team
from .models import TeamCreate, TeamUpdate
from modules.shared.response import success_response, error_response
from modules.auth.router import get_current_user

router = APIRouter()

@router.get("/")
async def list_teams():
    teams = await get_teams()
    return success_response(teams)

@router.get("/{team_id}")
async def get_team(team_id: int):
    team = await get_team_by_id(team_id)
    if not team:
        return error_response("Team not found", 404)
    return success_response(team)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_team(team: TeamCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    team_id = await create_team(team)
    return success_response({"team_id": team_id}, 201)

@router.put("/{team_id}", dependencies=[Depends(get_current_user)])
async def edit_team(team_id: int, team: TeamUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    updated = await update_team(team_id, team)
    if not updated:
        return error_response("Team not found", 404)
    return success_response({"message": "Team updated"})

@router.delete("/{team_id}", dependencies=[Depends(get_current_user)])
async def remove_team(team_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    deleted = await delete_team(team_id)
    if not deleted:
        return error_response("Team not found", 404)
    return success_response({"message": "Team deleted"})