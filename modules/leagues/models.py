from pydantic import BaseModel
from typing import Any, Optional

class LeagueCreate(BaseModel):
    league_name: str
    description: Optional[str] = None
    rules: Optional[str] = None
    settings: Optional[Any] = None

class LeagueUpdate(BaseModel):
    league_name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[str] = None
    settings: Optional[Any] = None