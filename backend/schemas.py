from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"
    verification_status: str = "pending"
    aadhar_path: Optional[str] = None
    degree_path: Optional[str] = None
    skill_certificate_path: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "student"

class UserUpdateRole(BaseModel):
    role: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class MaterialBase(BaseModel):
    title: str

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int
    course_id: int
    file_path: str
    upload_date: datetime

    class Config:
        from_attributes = True

class AssignmentBase(BaseModel):
    title: str
    description: str
    due_date: Optional[datetime] = None

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    id: int
    course_id: int
    file_path: Optional[str] = None

    class Config:
        from_attributes = True

class SubmissionBase(BaseModel):
    pass

class SubmissionCreate(SubmissionBase):
    pass

class Submission(SubmissionBase):
    id: int
    assignment_id: int
    student_id: int
    file_path: str
    submission_date: datetime
    grade: Optional[str] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: str
    instructor: str
    price: float
    duration: str

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    owner_id: Optional[int] = None
    materials: List[Material] = []
    assignments: List[Assignment] = []

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    course_id: int

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    booking_date: datetime
    status: str
    payment_status: str
    course: Course

    class Config:
        from_attributes = True

class UserWithBookings(User):
    bookings: List[Booking] = []
    courses: List[Course] = [] # Courses they own if tutor

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    booking_id: int
    amount: float

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int
    student_id: int
    student_name: Optional[str] = None
    course_title: Optional[str] = None
    payment_date: datetime
    status: str

    class Config:
        from_attributes = True

class TutorSalaryBase(BaseModel):
    tutor_id: int
    course_id: int
    amount: float

class TutorSalaryCreate(TutorSalaryBase):
    pass

class TutorSalaryOut(TutorSalaryBase):
    id: int
    tutor_name: Optional[str] = None
    course_title: Optional[str] = None
    payment_date: datetime
    status: str

    class Config:
        from_attributes = True
