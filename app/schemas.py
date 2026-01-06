# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import List
from datetime import date

# =====================================================
# USER AUTH
# =====================================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    total_xp: int

    class Config:
        from_attributes = True


# =====================================================
# SPEAKING / LESSON PROGRESS
# =====================================================

class SpeakingProgressRequest(BaseModel):
    user_id: int
    lesson_id: int
    dialogue_id: int
    score: int


# =====================================================
# GAME PROGRESS & XP (GENERIC)
# =====================================================

class ProgressUpdateRequest(BaseModel):
    user_id: int
    game_type: str   # "vocab", "speaking", "speed_race", etc.
    xp_earned: int
    score: int       # Raw score (ex: 8/10, 15 correct)


class ProgressUpdateResponse(BaseModel):
    total_xp: int
    current_streak: int
    streak_updated: bool
    message: str


# =====================================================
# WEEKLY ACTIVITY / ANALYTICS
# =====================================================

class WeeklyActivityItem(BaseModel):
    date: date
    xp: int
    day_name: str    # "Mon", "Tue", etc.


class WeeklyActivityResponse(BaseModel):
    activities: List[WeeklyActivityItem]
