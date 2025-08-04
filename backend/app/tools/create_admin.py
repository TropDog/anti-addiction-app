import uuid
import os
from app.core.database import SessionLocal
from app.modules.user.models import User
from app.core.security import hash_password
from dotenv import load_dotenv


load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def create_admin(email: str, password: str, addiction_type: str = "default"):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.commit()
                print(f"User {email} promoted to admin.")
            else:
                print(f"User {email} is already an admin.")
            return
        
        admin_user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hash_password(password),
            is_admin=True,
            addiction_type=addiction_type,
            failed_attempts=0,
            blocked_until=None
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user created with email: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin(ADMIN_EMAIL, ADMIN_PASSWORD)
