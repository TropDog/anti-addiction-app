from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from app.modules.user.models import User
from app.core.database import SessionLocal
from app.core.auth import get_current_user
from openai import OpenAI
import os

router = APIRouter()
load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_SECRET_KEY"))

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):#, user: User = Depends(get_current_user)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            prompt_messages = [
                {"role": "system", "content": "You are an empathetic therapist who supports the fight against addiction."},
                {"role": "user", "content": data}
            ]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=prompt_messages,
                temperature=0.7,
            )
            reply_text = response.choices[0].message.content
            await websocket.send_text(reply_text)
    except WebSocketDisconnect:
        print("User disconnected")