from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date, time, datetime

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

class AttackingStats(BaseModel):
    goals: int = 0
    assists: int = 0
    shots: int = 0
    shots_on_target: int = 0
    expected_goals: float = 0.0
    key_passes: int = 0
    dribbles: int = 0
    dribbles_successful: int = 0

class PossessionStats(BaseModel):
    possession_percentage: float = 0.0
    passes: int = 0
    passes_accurate: int = 0
    pass_accuracy: float = 0.0
    touches: int = 0
    crosses: int = 0
    crosses_accurate: int = 0

class DefensiveStats(BaseModel):
    tackles: int = 0
    tackles_won: int = 0
    interceptions: int = 0
    clearances: int = 0
    blocks: int = 0
    clean_sheet: bool = False

class DisciplinaryStats(BaseModel):
    fouls_committed: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    offsides: int = 0

class SetPieceStats(BaseModel):
    corners: int = 0
    free_kicks: int = 0

class GoalkeepingStats(BaseModel):
    saves: int = 0
    goals_conceded: int = 0
    distribution_accuracy: float = 0.0
    penalties_saved: int = 0

class TeamMatchStats(BaseModel):
    team_id: str
    attacking: AttackingStats = AttackingStats()
    possession: PossessionStats = PossessionStats()
    defensive: DefensiveStats = DefensiveStats()
    disciplinary: DisciplinaryStats = DisciplinaryStats()
    set_pieces: SetPieceStats = SetPieceStats()
    goalkeeping: GoalkeepingStats = GoalkeepingStats()

class MatchStatistics(BaseModel):
    match_id: str
    home_team_stats: TeamMatchStats
    away_team_stats: TeamMatchStats
    updated_at: Optional[datetime] = None

class UpdateMatchScore(BaseModel):
    home_score: int
    away_score: int
    status: Optional[str] = None  # e.g., "live", "finished", "scheduled"