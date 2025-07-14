from pydantic import BaseModel

class Standing(BaseModel):
    team_id: int
    team_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int