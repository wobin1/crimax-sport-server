from pydantic import BaseModel
from typing import Optional, Dict

class PlayerCreate(BaseModel):
    team_id: int
    first_name: str
    last_name: str
    photo: Optional[str] = None
    statistics: Optional[Dict] = None

class PlayerUpdate(BaseModel):
    team_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo: Optional[str] = None
    statistics: Optional[Dict] = None