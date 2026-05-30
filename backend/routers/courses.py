from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Course, User
from backend.schemas import Course as CourseSchema, CourseCreate
from backend.auth import RoleChecker, get_current_active_user

router = APIRouter()

allow_tutor_or_admin = RoleChecker(["tutor", "admin"])

from sqlalchemy import or_, and_

@router.get("/", response_model=List[CourseSchema])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Only show courses from admins and approved tutors
    courses = (
        db.query(Course)
        .join(User, Course.owner_id == User.id)
        .filter(
            or_(
                User.role == "admin",
                and_(User.role == "tutor", User.verification_status == "approved")
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return courses

@router.get("/my_created", response_model=List[CourseSchema])
def read_my_courses(db: Session = Depends(get_db), current_user: User = Depends(allow_tutor_or_admin)):
    if current_user.role == "admin":
        return db.query(Course).all()
    return db.query(Course).filter(Course.owner_id == current_user.id).all()

@router.post("/", response_model=CourseSchema)
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_tutor_or_admin)):
    # Tutors must be approved to create courses
    if current_user.role == "tutor" and current_user.verification_status != "approved":
        raise HTTPException(
            status_code=403, 
            detail="Your tutor account must be approved by an administrator before you can create courses."
        )
    
    db_course = Course(**course.model_dump(), owner_id=current_user.id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/{course_id}", response_model=CourseSchema)
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(allow_tutor_or_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this course")
        
    db.delete(course)
    db.commit()
    return {"detail": "Course deleted"}
