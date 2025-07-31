from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.auth import get_current_user
import app.modules.forms.models as models
import app.modules.forms.schemas as schemas


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

QUESTIONS = [
    {"id": "q1", "question": "Jak często odczuwasz potrzebę powrotu do nałogu?", "type": "scale", "scale": [1, 5]},
    {"id": "q2", "question": "Czy korzystasz z pomocy specjalisty?", "type": "choice", "choices": ["tak", "nie"]},
    {"id": "q3", "question": "Co było Twoim największym wyzwaniem w ostatnim tygodniu?", "type": "text"},
]

@router.get("/questions", tags=["forms"])
def get_questions():
    return {"questions": QUESTIONS}

@router.post("/submit", response_model=schemas.FormResponse)
def submit_form(
    form: schemas.FormSubmitRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    submission = models.FormSubmission(user_id=user.id, answers=form.answers)
    db.add(submission)
    db.commit()
    return {"message": "Formularz został zapisany pomyślnie"}