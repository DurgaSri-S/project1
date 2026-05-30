import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Material, Course, User, Booking
from backend.schemas import Material as MaterialSchema
from backend.auth import RoleChecker, get_current_active_user
from datetime import datetime

router = APIRouter()

allow_tutor_or_admin = RoleChecker(["tutor", "admin"])
UPLOAD_DIR = "uploads/materials/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=MaterialSchema)
def upload_material(
    course_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_tutor_or_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_material = Material(course_id=course_id, title=title, file_path=f"/api/files/materials/{filename}")
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@router.get("/course/{course_id}", response_model=List[MaterialSchema])
def get_course_materials(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "student":
        # Check if enrolled
        booking = db.query(Booking).filter(Booking.course_id == course_id, Booking.user_id == current_user.id).first()
        if not booking:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")

    return db.query(Material).filter(Material.course_id == course_id).all()
