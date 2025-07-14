from pydantic import BaseModel
from typing import Any

class LeagueCreate(BaseModel):
    league_name: str
    description: str | None = None
    rules: str | None = None
    settings: Any | None = None