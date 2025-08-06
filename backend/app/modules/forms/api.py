from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.auth import get_current_user
from app.modules.user.models import User
import app.modules.forms.models as models
import app.modules.forms.schemas as schemas
from uuid import UUID


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/addiction/active/form", tags=["forms"])
def get_active_form(db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    form = db.query(models.FormType).filter(
        models.FormType.addiction_type == user.addiction_type,
        models.FormType.is_active == True
    ).first()

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return {
        "id": form.id,
        "name": form.name,
        "description": form.description,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "type": q.type,
                "options": q.options,
                "required": q.required
            } for q in form.questions
        ]
    }

@router.post("/{form_id}/answers", tags=["forms"])
def submit_answers(form_id: UUID,
                   data: schemas.AnswerSubmitSchema,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    
    form = db.query(models.FormType).filter(models.FormType.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    for answer_data in data.answers:
        db.add(models.Answer(
            form_id=form_id,
            user_id=current_user.id,
            question_id=answer_data.question_id,
            value=answer_data.value
        ))

    db.commit()
    return {"status": "saved"}

@router.get("/{form_id}/answers", tags=["forms"])
def get_user_answers(form_id: UUID,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    answers = db.query(models.Answer).filter(
        models.Answer.form_id == form_id,
        models.Answer.user_id == current_user.id
    ).all()

    return [
        {
            "question_id": a.question_id,
            "value": a.value,
            "created_at": a.created_at
        } for a in answers
    ]