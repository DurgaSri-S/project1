import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Submission, Assignment, Course, User, Booking
from backend.schemas import Submission as SubmissionSchema
from backend.auth import RoleChecker, get_current_active_user
from datetime import datetime

router = APIRouter()

allow_tutor_or_admin = RoleChecker(["tutor", "admin"])
UPLOAD_DIR = "uploads/submissions/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/assignment/{assignment_id}", response_model=SubmissionSchema)
def create_submission(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    booking = db.query(Booking).filter(Booking.course_id == assignment.course_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=403, detail="Not enrolled")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{current_user.id}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_sub = Submission(
        assignment_id=assignment.id,
        student_id=current_user.id,
        file_path=f"/api/files/submissions/{filename}"
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.get("/assignment/{assignment_id}", response_model=List[SubmissionSchema])
def get_submissions_for_assignment(assignment_id: int, db: Session = Depends(get_db), current_user: User = Depends(allow_tutor_or_admin)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if current_user.role != "admin" and course.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(Submission).filter(Submission.assignment_id == assignment_id).all()

@router.put("/{submission_id}/grade", response_model=SubmissionSchema)
def grade_submission(submission_id: int, grade: str, feedback: str = "", db: Session = Depends(get_db), current_user: User = Depends(allow_tutor_or_admin)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    course = sub.assignment.course
    if current_user.role != "admin" and course.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    sub.grade = grade
    sub.feedback = feedback
    db.commit()
    db.refresh(sub)
    return sub
