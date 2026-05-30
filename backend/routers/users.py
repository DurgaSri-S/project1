from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import os
import shutil
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List

from backend.database import get_db
from backend.models import User
from backend.schemas import User as UserSchema, UserCreate, UserUpdateRole, Token
from backend.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_user_by_email, get_current_active_user, RoleChecker

router = APIRouter()

allow_admin = RoleChecker(["admin"])
VERIFY_DIR = "uploads/verification/"
os.makedirs(VERIFY_DIR, exist_ok=True)

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    role = user.role or "student"
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=role,
        verification_status="approved" if role == "student" else "unverified"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Admin endpoints
@router.get("/", response_model=List[UserSchema])
def get_all_users(db: Session = Depends(get_db), _: User = Depends(allow_admin)):
    return db.query(User).all()

@router.put("/{user_id}/role", response_model=UserSchema)
def update_user_role(user_id: int, role_update: UserUpdateRole, db: Session = Depends(get_db), _: User = Depends(allow_admin)):
    if role_update.role not in ["student", "tutor", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role specified")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user

@router.put("/verify/upload", response_model=UserSchema)
def upload_verification(
    aadhar: UploadFile = File(None),
    degree: UploadFile = File(None),
    skill_certificate: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not aadhar and not degree and not skill_certificate:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    if aadhar:
        filename = f"{current_user.id}_aadhar_{timestamp}_{aadhar.filename.replace(' ', '_')}"
        file_path = os.path.join(VERIFY_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(aadhar.file, buffer)
        current_user.aadhar_path = f"/api/files/verification/{filename}"
        
    if degree:
        filename = f"{current_user.id}_degree_{timestamp}_{degree.filename.replace(' ', '_')}"
        file_path = os.path.join(VERIFY_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(degree.file, buffer)
        current_user.degree_path = f"/api/files/verification/{filename}"

    if skill_certificate:
        filename = f"{current_user.id}_skill_{timestamp}_{skill_certificate.filename.replace(' ', '_')}"
        file_path = os.path.join(VERIFY_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(skill_certificate.file, buffer)
        current_user.skill_certificate_path = f"/api/files/verification/{filename}"
    
    # Update status logic
    if current_user.role == "tutor":
        # Tutors need all three to move to pending
        if current_user.aadhar_path and current_user.degree_path and current_user.skill_certificate_path:
            current_user.verification_status = "pending"
    else:
        # Students/others only need one to move to pending if they are trying to verify
        current_user.verification_status = "pending"
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/{user_id}/verify/approve", response_model=UserSchema)
def approve_verification(user_id: int, db: Session = Depends(get_db), _: User = Depends(allow_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.verification_status = "approved"
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/verify/reject", response_model=UserSchema)
def reject_verification(user_id: int, db: Session = Depends(get_db), _: User = Depends(allow_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.verification_status = "rejected"
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(allow_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}
