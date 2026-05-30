import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import User
from backend.auth import get_password_hash

Base.metadata.create_all(bind=engine)

def seed_admin():
    db: Session = SessionLocal()
    admin_email = "admin@nexustech.com"
    existing = db.query(User).filter(User.email == admin_email).first()
    if not existing:
        hashed = get_password_hash("admin123")
        admin = User(
            email=admin_email,
            full_name="System Administrator",
            hashed_password=hashed,
            role="admin"
        )
        db.add(admin)
        db.commit()
        print(f"Created admin user: {admin_email} / admin123")
    else:
        existing.role = "admin"
        db.commit()
        print(f"Admin user already exists: {admin_email}")
    db.close()

if __name__ == "__main__":
    seed_admin()
