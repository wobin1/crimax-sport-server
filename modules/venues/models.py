from pydantic import BaseModel
from typing import Optional

class VenueCreate(BaseModel):
    venue_name: str
    address: Optional[str] = None
    capacity: Optional[int] = None

class VenueUpdate(BaseModel):
    venue_name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
