from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.database import engine, Base
from backend.routers import users, courses, bookings, materials, assignments, submissions, payments

# Create DB Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Online Course Reservation API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Let's mount the API routers under /api namespace
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(materials.router, prefix="/api/materials", tags=["materials"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["assignments"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["submissions"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])

# Mount uploads directory for file serving
uploads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_path, exist_ok=True)
app.mount("/api/files", StaticFiles(directory=uploads_path), name="uploads")

# Mount frontend

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
os.makedirs(frontend_path, exist_ok=True)
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
