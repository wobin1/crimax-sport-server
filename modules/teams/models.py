from pydantic import BaseModel
from typing import Optional, Dict

class TeamCreate(BaseModel):
    league_id: int
    division_id: Optional[int] = None
    team_name: str
    logo: Optional[str] = None
    contact_info: Optional[Dict] = None

class TeamUpdate(BaseModel):
    league_id: Optional[int] = None
    division_id: Optional[int] = None
    team_name: Optional[str] = None
    logo: Optional[str] = None
    contact_info: Optional[Dict] = None