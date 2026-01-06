from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, database, utils
from pydantic import BaseModel

router = APIRouter(tags=["Authentication"])

get_db = database.get_db

# ==========================================
# 1. DATA MODELS
# ==========================================

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: int
    xp: int

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    total_xp: int

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    # We keep 'otp' here so the Android app doesn't crash sending it, 
    # but we will IGNORE it in the logic.
    otp: str = "" 
    new_password: str
    

class SimpleResponse(BaseModel):
    message: str
    success: bool
    
    
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str    


# --- Profile Models ---
class UserProfileResponse(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    phone_number: str | None = None

class UpdateProfileRequest(BaseModel):
    full_name: str
    username: str
    email: str
    phone_number: str    

# ==========================================
# 2. ROUTES
# ==========================================

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Check if email exists
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash the password
    hashed_pwd = utils.hash_password(request.password)
    
    # 3. Save to DB
    new_user = models.User(
        email=request.email, 
        username=request.username, 
        hashed_password=hashed_pwd,
        total_xp=0,
        current_streak=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RegisterResponse(
        id=new_user.id, 
        username=new_user.username, 
        email=new_user.email, 
        total_xp=new_user.total_xp
    )

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    # 2. Check password
    if not user or not utils.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    return LoginResponse(
        message="Login Successful",
        user_id=user.id,
        xp=user.total_xp
    )
    
@router.get("/profile/{user_id}", response_model=UserProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number
    )

@router.put("/profile/{user_id}", response_model=SimpleResponse)
def update_profile(user_id: int, request: UpdateProfileRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if new email/username is taken by someone else
    existing = db.query(models.User).filter(
        ((models.User.email == request.email) | (models.User.username == request.username)) & 
        (models.User.id != user_id)
    ).first()
    
    if existing:
        return SimpleResponse(message="Username or Email already taken", success=False)

    # Update fields
    user.full_name = request.full_name
    user.username = request.username
    user.email = request.email
    user.phone_number = request.phone_number
    
    db.commit()
    return SimpleResponse(message="Profile updated successfully!", success=True)

# ==========================================
# ⚡ DIRECT RESET LOGIC (NO OTP)
# ==========================================

@router.post("/auth/forgot-password", response_model=SimpleResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Direct Logic:
    If the email is in the database, return Success immediately.
    We do NOT send an email. We do NOT generate an OTP.
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        # If user doesn't exist, we say "Failed"
        return SimpleResponse(message="Email address not found.", success=False)

    # If user exists, we say "Success" (This allows the App to move to the Reset Screen)
    return SimpleResponse(message="User verified. Please reset password.", success=True)


@router.post("/auth/reset-password", response_model=SimpleResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Updates the password directly.
    We IGNORE the 'otp' field sent by the app.
    """
    # 1. Find User
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        return SimpleResponse(message="User not found.", success=False)

    # 2. Hash the New Password (IMPORTANT!)
    hashed_new_pwd = utils.hash_password(request.new_password)

    # 3. Update Database
    user.hashed_password = hashed_new_pwd
    db.commit()

    return SimpleResponse(message="Password changed successfully!", success=True)

@router.post("/auth/change-password/{user_id}", response_model=SimpleResponse)
def change_password(user_id: int, request: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 1. Verify Old Password
    if not utils.verify_password(request.old_password, user.hashed_password):
        return SimpleResponse(message="Incorrect old password", success=False)
    
    # 2. Hash New Password
    user.hashed_password = utils.hash_password(request.new_password)
    db.commit()
    
    return SimpleResponse(message="Password updated successfully!", success=True)

@router.delete("/auth/delete-account/{user_id}", response_model=SimpleResponse)
def delete_account(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return SimpleResponse(message="Account deleted.", success=True)