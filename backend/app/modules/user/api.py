from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.user.models import User
from app.modules.user.schemas import UserRegister, LoginRequest, TokenResponse
from app.core.security import hash_password
from app.core.auth import authenticate_user, create_access_token, get_current_user


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/api/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_pwd,
        addiction_type=user.addiction_type
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User successfully registered", "user_id": str(new_user.id)}

@router.post("/api/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, data.email, data.password)
    except HTTPException as e:
        raise e
    token = create_access_token({"sub": user.email})
    return {"access_token": token}

@router.get("/protected")
def protected_endpoint(user=Depends(get_current_user)):
    return {"message": "You are authenticated", "user": user}