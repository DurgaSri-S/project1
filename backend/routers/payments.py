from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, Course, Booking, Payment, TutorSalary
from backend.schemas import PaymentOut, PaymentCreate, TutorSalaryOut, TutorSalaryCreate
from backend.auth import get_current_user

router = APIRouter()

@router.post("/enroll", response_model=PaymentOut)
def process_student_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can enroll and pay")
    
    booking = db.query(Booking).filter(Booking.id == payment.booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Process payment
    new_payment = Payment(
        booking_id=payment.booking_id,
        student_id=current_user.id,
        amount=payment.amount,
        status="completed"
    )
    db.add(new_payment)
    
    # Update booking payment status
    booking.payment_status = "paid"
    
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.get("/admin/revenue", response_model=List[PaymentOut])
def get_all_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view revenue")
    
    payments = db.query(Payment, User.full_name, Course.title).join(
        User, Payment.student_id == User.id
    ).join(
        Booking, Payment.booking_id == Booking.id
    ).join(
        Course, Booking.course_id == Course.id
    ).all()
    
    result = []
    for p, name, title in payments:
        out = PaymentOut.from_orm(p)
        out.student_name = name
        out.course_title = title
        result.append(out)
    return result

@router.get("/admin/salaries", response_model=List[TutorSalaryOut])
def get_tutor_salaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view salaries")
    
    salaries = db.query(TutorSalary, User.full_name, Course.title).join(
        User, TutorSalary.tutor_id == User.id
    ).join(
        Course, TutorSalary.course_id == Course.id
    ).all()

    result = []
    for s, name, title in salaries:
        out = TutorSalaryOut.from_orm(s)
        out.tutor_name = name
        out.course_title = title
        result.append(out)
    return result

@router.post("/admin/pay_tutor", response_model=TutorSalaryOut)
def pay_tutor_salary(
    salary: TutorSalaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can pay salaries")
    
    course = db.query(Course).filter(Course.id == salary.course_id).first()
    if not course or course.owner_id != salary.tutor_id:
        raise HTTPException(status_code=400, detail="Invalid course or tutor assignment")

    new_salary = TutorSalary(
        tutor_id=salary.tutor_id,
        course_id=salary.course_id,
        amount=salary.amount,
        status="paid"
    )
    db.add(new_salary)
    db.commit()
    db.refresh(new_salary)
    return new_salary
