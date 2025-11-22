from pydantic import BaseModel
from typing import Optional
from datetime import date

class SeasonCreate(BaseModel):
    league_id: int
    season_name: str
    start_date: date
    end_date: date

class SeasonUpdate(BaseModel):
    league_id: Optional[int] = None
    season_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
