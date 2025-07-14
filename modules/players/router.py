from fastapi import APIRouter, Depends, HTTPException
from .manager import get_players, get_player_by_id, create_player, update_player, delete_player
from .models import PlayerCreate, PlayerUpdate
from modules.shared.response import success_response, error_response
from modules.auth.router import get_current_user

router = APIRouter()

@router.get("/", dependencies=[Depends(get_current_user)])
async def list_players():
    players = await get_players()
    return success_response(players)

@router.get("/{player_id}", dependencies=[Depends(get_current_user)])
async def get_player(player_id: int):
    player = await get_player_by_id(player_id)
    if not player:
        return error_response("Player not found", 404)
    return success_response(player)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_player(player: PlayerCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    player_id = await create_player(player)
    return success_response({"player_id": player_id}, 201)

@router.put("/{player_id}", dependencies=[Depends(get_current_user)])
async def edit_player(player_id: int, player: PlayerUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    updated = await update_player(player_id, player)
    if not updated:
        return error_response("Player not found", 404)
    return success_response({"message": "Player updated"})

@router.delete("/{player_id}", dependencies=[Depends(get_current_user)])
async def remove_player(player_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    deleted = await delete_player(player_id)
    if not deleted:
        return error_response("Player not found", 404)
    return success_response({"message": "Player deleted"})