from fastapi import APIRouter, Depends, HTTPException
from .manager import get_matches, get_match_by_id, create_match, update_match, delete_match
from .models import MatchCreate, MatchUpdate
from modules.shared.response import success_response, error_response
from modules.auth.router import get_current_user
import json

router = APIRouter()

@router.get("/")
async def list_matches():
    matches = await get_matches()
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