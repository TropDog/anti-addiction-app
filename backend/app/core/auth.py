from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.modules.user.models import User
from app.core.database import SessionLocal
from jose import JWTError
import app.core.security as security
import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
MAX_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS"))
BLOCK_TIME = int(os.getenv("BLOCK_TIME")) 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, email: str, password: str):
    
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

def verify_and_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if not exp:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has no expiry")

        expire_time = datetime.utcfromtimestamp(exp)
        now = datetime.utcnow()
        if expire_time < now:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")

        new_expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload["exp"] = new_expire.timestamp()

        refreshed_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return payload, refreshed_token

    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security.bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload, refreshed_token = verify_and_refresh_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except JWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

def get_current_admin(user = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin access required'
        )
    return user



