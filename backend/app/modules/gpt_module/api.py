from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from app.modules.user.models import User
from app.modules.gpt_module.models import Chat
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.modules.gpt_module.services import handle_chat_logic
from openai import OpenAI
from uuid import UUID
import os
import app.modules.gpt_module.services as gpt_services
from datetime import datetime
router = APIRouter()
load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_SECRET_KEY"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/start-chat/{user_id}")
def start_chat(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    new_chat = Chat(
        user_id=user.id,
        title = f"Therapy Chat {datetime.utcnow().isoformat()}"
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return {"chat_id": str(new_chat.id)}

@router.websocket("/ws/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: UUID, db: Session = Depends(get_db)):
    try:
        await handle_chat_logic(websocket, db, chat_id)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected chat_id={chat_id}")