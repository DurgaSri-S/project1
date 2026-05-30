import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import Assignment, Course, User, Booking
from backend.schemas import Assignment as AssignmentSchema
from backend.auth import RoleChecker, get_current_active_user

router = APIRouter()

allow_tutor_or_admin = RoleChecker(["tutor", "admin"])
UPLOAD_DIR = "uploads/assignments/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=AssignmentSchema)
def create_assignment(
    course_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    due_date: str = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_tutor_or_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_assignment = Assignment(
        course_id=course_id,
        title=title,
        description=description,
        due_date=datetime.fromisoformat(due_date) if due_date and due_date != "null" else None
    )

    if file:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        db_assignment.file_path = f"/api/files/assignments/{filename}"

    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.get("/course/{course_id}", response_model=List[AssignmentSchema])
def get_course_assignments(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "student":
        booking = db.query(Booking).filter(Booking.course_id == course_id, Booking.user_id == current_user.id).first()
        if not booking or booking.payment_status != "paid":
            raise HTTPException(status_code=403, detail="Payment required to view assignments")

    return db.query(Assignment).filter(Assignment.course_id == course_id).all()
