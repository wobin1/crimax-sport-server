from fastapi import APIRouter, Depends, HTTPException
from .manager import get_matches, get_match_by_id, create_match, update_match, delete_match
from .models import MatchCreate, MatchUpdate, MatchStatistics, UpdateMatchScore, TeamMatchStats
from modules.shared.response import success_response, error_response
from modules.auth.router import get_current_user
from .manager import MatchManager
from ..shared.db import get_db_connection
import json

router = APIRouter()

async def get_match_manager():
    """Dependency to get MatchManager instance"""
    db = await get_db_connection()
    return MatchManager(db)

@router.get("/")
async def list_matches(season_id: int = None):
    matches = await get_matches(season_id)
    return success_response(matches)

@router.get("/{match_id}")
async def get_match(match_id: int):
    match = await get_match_by_id(match_id)
    if not match:
        return error_response("Match not found", 404)
    return success_response(match)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_match(match: MatchCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    match_id = await create_match(match)
    return success_response({"match_id": match_id}, 201)

@router.put("/{match_id}", dependencies=[Depends(get_current_user)])
async def edit_match(match_id: int, match: MatchUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "team_manager"]:
        return error_response("Unauthorized", 403)
    updated = await update_match(match_id, match)
    if not updated:
        return error_response("Match not found", 404)
    return success_response({"message": "Match updated"})

@router.delete("/{match_id}", dependencies=[Depends(get_current_user)])
async def remove_match(match_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    deleted = await delete_match(match_id)
    if not deleted:
        return error_response("Match not found", 404)
    return success_response({"message": "Match deleted"})

@router.put("/{match_id}/score")
async def update_match_score(
    match_id: str,
    score_update: UpdateMatchScore,
    manager: MatchManager = Depends(get_match_manager)
):
    """Update match score and status"""
    result = await manager.update_match_score(match_id, score_update)
    if not result:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"message": "Match score updated successfully", "data": result}

@router.post("/{match_id}/statistics")
async def create_or_update_match_statistics(
    match_id: int,
    statistics: MatchStatistics,
    manager: MatchManager = Depends(get_match_manager)
):
    """Create or update match statistics"""
    # Verify match exists
    match = await manager.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    result = await manager.create_or_update_match_statistics(match_id, statistics)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update statistics")
    return {"message": "Match statistics updated successfully", "data": result}

@router.get("/{match_id}/statistics")
async def get_match_statistics(
    match_id: int,
    manager: MatchManager = Depends(get_match_manager)
):
    """Get match statistics"""
    result = await manager.get_match_statistics(match_id)
    if not result:
        raise HTTPException(status_code=404, detail="Match statistics not found")
    return {"data": result}

@router.get("/{match_id}/stats")
async def get_match_stats(match_id: int, manager: MatchManager = Depends(get_match_manager)):
    """Get match statistics (alias endpoint)"""
    # Try to get from match_statistics table first
    result = await manager.get_match_statistics(match_id)
    
    if result:
        # Parse the JSON strings back to objects
        import json
        home_stats = json.loads(result.get("home_team_stats", "{}")) if isinstance(result.get("home_team_stats"), str) else result.get("home_team_stats", {})
        away_stats = json.loads(result.get("away_team_stats", "{}")) if isinstance(result.get("away_team_stats"), str) else result.get("away_team_stats", {})
        
        return success_response({
            "home_team_stats": home_stats,
            "away_team_stats": away_stats
        })
    
    # Fallback to checking match results field
    conn = await get_db_connection()
    try:
        match = await get_match_by_id(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        results = match.get("results", {})
        if results and isinstance(results, dict):
            stats = {
                "home_team_stats": results.get("home_team_stats", {}),
                "away_team_stats": results.get("away_team_stats", {})
            }
            return success_response(stats)
        
        # Return empty stats if no data
        return success_response({
            "home_team_stats": {},
            "away_team_stats": {}
        })
    finally:
        await conn.close()

@router.get("/{match_id}/goals")
async def get_match_goals(match_id: int):
    """Get all goals for a specific match"""
    conn = await get_db_connection()
    try:
        goals = await conn.fetch("""
            SELECT 
                mg.id,
                mg.match_id,
                mg.player_id,
                p.first_name || ' ' || p.last_name as player_name,
                mg.team_id,
                t.team_name,
                mg.minute,
                mg.goal_type,
                mg.created_at
            FROM match_goals mg
            LEFT JOIN players p ON mg.player_id = p.player_id
            LEFT JOIN teams t ON mg.team_id = t.team_id
            WHERE mg.match_id = $1
            ORDER BY mg.minute ASC
        """, match_id)
        
        goals_list = [
            {
                "id": goal["id"],
                "match_id": goal["match_id"],
                "player_id": goal["player_id"],
                "player_name": goal["player_name"],
                "team_id": goal["team_id"],
                "team_name": goal["team_name"],
                "minute": goal["minute"],
                "goal_type": goal["goal_type"],
                "created_at": goal["created_at"].isoformat() if goal["created_at"] else None
            }
            for goal in goals
        ]
        
        return success_response(goals_list)
    finally:
        await conn.close()

@router.post("/{match_id}/goals")
async def add_match_goal(
    match_id: int,
    player_id: int,
    team_id: int,
    minute: int,
    goal_type: str = 'regular'
):
    """Add a goal to a match (scores calculated automatically from match_goals)"""
    conn = await get_db_connection()
    try:
        # Verify match exists
        match = await conn.fetchrow("""
            SELECT team1_id, team2_id
            FROM matches
            WHERE match_id = $1
        """, match_id)
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Insert the goal
        goal_id = await conn.fetchval("""
            INSERT INTO match_goals (match_id, player_id, team_id, minute, goal_type, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            RETURNING id
        """, match_id, player_id, team_id, minute, goal_type)
        
        # Count total goals for each team (for response only)
        home_goals = await conn.fetchval("""
            SELECT COUNT(*) FROM match_goals
            WHERE match_id = $1 AND team_id = $2
        """, match_id, match["team1_id"])
        
        away_goals = await conn.fetchval("""
            SELECT COUNT(*) FROM match_goals
            WHERE match_id = $1 AND team_id = $2
        """, match_id, match["team2_id"])
        
        return success_response({
            "id": goal_id,
            "message": "Goal added successfully",
            "home_score": home_goals,
            "away_score": away_goals
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add goal: {str(e)}")
    finally:
        await conn.close()

@router.delete("/goals/{goal_id}")
async def delete_match_goal(goal_id: int):
    """Delete a goal (scores calculated automatically from match_goals)"""
    conn = await get_db_connection()
    try:
        # Get goal details before deleting
        goal = await conn.fetchrow("SELECT match_id FROM match_goals WHERE id = $1", goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        match_id = goal["match_id"]
        
        # Delete the goal
        result = await conn.execute("DELETE FROM match_goals WHERE id = $1", goal_id)
        
        if result == "DELETE 1":
            # Get match details
            match = await conn.fetchrow("""
                SELECT team1_id, team2_id
                FROM matches
                WHERE match_id = $1
            """, match_id)
            
            # Recalculate goals for each team (for response only)
            home_goals = await conn.fetchval("""
                SELECT COUNT(*) FROM match_goals
                WHERE match_id = $1 AND team_id = $2
            """, match_id, match["team1_id"])
            
            away_goals = await conn.fetchval("""
                SELECT COUNT(*) FROM match_goals
                WHERE match_id = $1 AND team_id = $2
            """, match_id, match["team2_id"])
            
            return success_response({
                "message": "Goal deleted successfully",
                "home_score": home_goals,
                "away_score": away_goals
            })
        else:
            raise HTTPException(status_code=404, detail="Goal not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete goal: {str(e)}")
    finally:
        await conn.close()