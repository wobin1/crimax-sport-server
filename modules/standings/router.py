from fastapi import APIRouter
from .manager import get_league_standings
from modules.shared.response import success_response, error_response

router = APIRouter()

@router.get("/{league_id}")
async def list_standings(league_id: int):
    standings = await get_league_standings(league_id)
    if not standings:
        return error_response("No standings available for this league", 404)
    return success_response(standings)