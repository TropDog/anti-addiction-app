from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
import app.core.security as security
import jwt
import os
import time

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
MAX_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS"))
BLOCK_TIME = int(os.getenv("BLOCK_TIME")) 

def authenticate_user(db: Session, email: str, password: str):
    from app.models.user import User 
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.blocked_until and datetime.utcnow() < user.blocked_until:
        remaining = int((user.blocked_until - datetime.utcnow()).total_seconds())
        raise HTTPException(
            status_code=403,
            detail=f"Account locked. Try again in {remaining} seconds."
        )

    if not security.verify_password(password, user.hashed_password):
        user.failed_attempts += 1
        if user.failed_attempts >= MAX_ATTEMPTS:
            user.blocked_until = datetime.utcnow() + timedelta(minutes=BLOCK_TIME)
            user.failed_attempts = 0 
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.failed_attempts = 0
    user.blocked_until = None
    db.commit()
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



