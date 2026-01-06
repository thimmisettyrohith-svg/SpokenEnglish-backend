from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ProgressUpdateRequest, ProgressUpdateResponse, WeeklyActivityResponse
from ..services import progress_service

router = APIRouter(prefix="/progress", tags=["Progress & Stats"])

@router.post("/update", response_model=ProgressUpdateResponse)
def update_progress(request: ProgressUpdateRequest, db: Session = Depends(get_db)):
    """
    Call this when a game finishes. 
    It updates XP, calculates Streak, and logs daily activity.
    """
    return progress_service.update_user_xp_and_streak(
        db=db,
        user_id=request.user_id,
        xp=request.xp_earned
    )

@router.get("/{user_id}/weekly", response_model=WeeklyActivityResponse)
def get_weekly_stats(user_id: int, db: Session = Depends(get_db)):
    """
    Returns XP earned over the last 7 days for the Profile Graph.
    """
    data = progress_service.get_weekly_activity(db, user_id)
    return {"activities": data}