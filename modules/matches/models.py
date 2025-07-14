from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date, time

class MatchCreate(BaseModel):
    season_id: int
    team1_id: int
    team2_id: int
    venue_id: Optional[int] = None
    date: date
    time: time
    results: Optional[Dict] = None

class MatchUpdate(BaseModel):
    season_id: Optional[int] = None
    team1_id: Optional[int] = None
    team2_id: Optional[int] = None
    venue_id: Optional[int] = None
    date: Optional[date] = None
    time: Optional[time] = None
    results: Optional[Dict] = None