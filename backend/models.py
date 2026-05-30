from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="student") # student, tutor, admin
    
    # Verification fields
    verification_status = Column(String, default="pending") # pending, approved, rejected
    aadhar_path = Column(String, nullable=True)
    degree_path = Column(String, nullable=True) # for tutors
    skill_certificate_path = Column(String, nullable=True)

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="owner", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Admin or Tutor who created it
    title = Column(String, index=True)
    description = Column(String)
    instructor = Column(String)
    price = Column(Float)
    duration = Column(String)

    owner = relationship("User", back_populates="courses")
    bookings = relationship("Booking", back_populates="course")
    materials = relationship("Material", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    course = relationship("Course", back_populates="materials")

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    description = Column(String)
    file_path = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    submission_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    grade = Column(String, nullable=True)
    feedback = Column(String, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    booking_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="confirmed")
    payment_status = Column(String, default="paid")


    user = relationship("User", back_populates="bookings")
    course = relationship("Course", back_populates="bookings")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="completed")

    booking = relationship("Booking")
    student = relationship("User")

class TutorSalary(Base):
    __tablename__ = "tutor_salaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    amount = Column(Float)
    payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="paid")

    tutor = relationship("User")
    course = relationship("Course")
