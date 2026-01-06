from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models import User, UserActivity
from fastapi import HTTPException

def update_user_xp_and_streak(db: Session, user_id: int, xp: int):
    # 1. Fetch User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = date.today()
    streak_updated = False

    # 2. Update XP
    user.total_xp += xp

    # 3. Streak Logic
    last_active = user.last_active_date

    if last_active == today:
        # Already played today, just keep streak
        pass
    elif last_active == today - timedelta(days=1):
        # Played yesterday -> Streak continues!
        user.current_streak += 1
        user.last_active_date = today
        streak_updated = True
    else:
        # Missed a day (or new user) -> Reset streak
        user.current_streak = 1
        user.last_active_date = today
        streak_updated = True

    # 4. Update Daily Activity Log (For the Graph)
    # Check if we already have an entry for TODAY
    daily_log = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.activity_date == today
    ).first()

    if daily_log:
        daily_log.xp_earned += xp
    else:
        new_log = UserActivity(user_id=user_id, xp_earned=xp, activity_date=today)
        db.add(new_log)

    db.commit()
    db.refresh(user)

    return {
        "total_xp": user.total_xp,
        "current_streak": user.current_streak,
        "streak_updated": streak_updated,
        "message": "Progress saved successfully"
    }

def get_weekly_activity(db: Session, user_id: int):
    # Get last 7 days including today
    today = date.today()
    start_date = today - timedelta(days=6)

    logs = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.activity_date >= start_date
    ).all()

    # Map existing logs to a dictionary {date: xp}
    log_map = {log.activity_date: log.xp_earned for log in logs}

    result = []
    # Loop through last 7 days to ensure even 0 XP days are shown
    for i in range(7):
        current_day = start_date + timedelta(days=i)
        xp = log_map.get(current_day, 0)
        day_name = current_day.strftime("%a") # "Mon", "Tue"
        
        result.append({
            "date": current_day,
            "xp": xp,
            "day_name": day_name
        })

    return result