from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models import Booking, Course, User
from backend.schemas import Booking as BookingSchema, BookingCreate
from backend.auth import get_current_active_user, RoleChecker

router = APIRouter()

allow_admin = RoleChecker(["admin"])

@router.post("/", response_model=BookingSchema)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    course = db.query(Course).filter(Course.id == booking.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Check enrollment limit (Maximum 3 courses)
    enrollment_count = db.query(Booking).filter(Booking.user_id == current_user.id).count()
    if enrollment_count >= 3:
        raise HTTPException(
            status_code=400, 
            detail="Enrollment limit reached. You can only enroll in a maximum of 3 courses."
        )
        
    existing_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.course_id == booking.course_id
    ).first()
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="Already booked this course")

    db_booking = Booking(
        user_id=current_user.id,
        course_id=booking.course_id,
        booking_date=datetime.utcnow(),
        status="confirmed",
        payment_status="pending"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/my_bookings", response_model=List[BookingSchema])
def read_my_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return db.query(Booking).filter(Booking.user_id == current_user.id).all()

@router.get("/all", response_model=List[BookingSchema])
def read_all_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(allow_admin)):
    bookings = db.query(Booking).offset(skip).limit(limit).all()
    return bookings
