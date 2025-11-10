from fastapi import APIRouter, Depends, HTTPException
from .manager import get_venues, get_venue_by_id, create_venue, update_venue, delete_venue
from .models import VenueCreate, VenueUpdate
from modules.shared.response import success_response
from modules.auth.router import get_current_user

router = APIRouter()

@router.get("/")
async def list_venues():
    venues = await get_venues()
    return success_response(venues)

@router.get("/{venue_id}")
async def get_venue(venue_id: int):
    venue = await get_venue_by_id(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return success_response(venue)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_venue(venue: VenueCreate):
    venue_id = await create_venue(venue)
    return success_response({"venue_id": venue_id})

@router.put("/{venue_id}", dependencies=[Depends(get_current_user)])
async def edit_venue(venue_id: int, venue: VenueUpdate):
    success = await update_venue(venue_id, venue)
    if not success:
        raise HTTPException(status_code=404, detail="Venue not found")
    updated_venue = await get_venue_by_id(venue_id)
    return success_response(updated_venue)

@router.delete("/{venue_id}", dependencies=[Depends(get_current_user)])
async def remove_venue(venue_id: int):
    success = await delete_venue(venue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Venue not found")
    return success_response({"message": "Venue deleted successfully"})
