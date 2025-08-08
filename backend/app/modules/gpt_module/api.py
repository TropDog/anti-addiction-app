from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from app.modules.user.models import User
from app.core.database import SessionLocal
from app.core.auth import get_current_user
from openai import OpenAI
import os

router = APIRouter()
load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_SECRET_KEY"))

@router.post("/chat")
async def chat_with_gpt(user: User = Depends(get_current_user)):
    msg = f'Cześć, to jest moja pierwsza próba komunikacji z Tobą. W danych moje uzależnienie jest określone jako:{user.addiction_type}. Odpowiedz mi w trzech zdaniach jaki mam problem'
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś empatycznym terapeutą wspierającym walkę z nałogami."},
            {"role": "user", "content": msg}
        ],
        temperature=0.7, 
    )
    return {"reply": response.choices[0].message.content}