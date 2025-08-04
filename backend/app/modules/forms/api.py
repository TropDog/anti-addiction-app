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


@router.get("/types/all", tags=["forms"])
def get_all_forms(db: Session = Depends(get_db)):
    forms = db.query(models.FormType).all()
    return forms

@router.get("/questions/{form_id}", tags=["forms"])
def get_questions(form_id: UUID,
                  db:  Session = Depends(get_db)):
    form = db.query(models.FormType).filter(models.FormType.id == form_id).first()
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
def submit_answers(form_id: UUID, data: schemas.AnswerSchema, current_user: User = Depends(get_current_user)):
    db = Session(Depends=get_db)
    form = db.query(models.FormType).filter(models.FormType.form_id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    answer = models.Answer(
        form_id=form_id,
        user_id=current_user.id,
        answers=data.answers
    )

    db.add(answer)
    db.commit()
    db.refresh(answer)
    return {"id": answer.id, "status": "saved"}