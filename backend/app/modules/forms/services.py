from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.modules.forms.models import FormType, Question
from app.modules.forms.schemas import FormCreate
from fastapi import HTTPException
from uuid import UUID

def create_form_service(db: Session, form_data: FormCreate) -> FormType:
    
    q1 = db.execute(select(FormType).filter_by(name=form_data.name))
    if q1.scalars().first():
        raise ValueError("Form with this name already exists.")

    if form_data.is_active:
        active_forms = db.execute(
            select(FormType).filter_by(addiction_type=form_data.addiction_type, is_active=True)
        )
        for form in active_forms.scalars():
            form.is_active = False

    new_form = FormType(
        addiction_type=form_data.addiction_type,
        name=form_data.name,
        description=form_data.description,
        is_active=True,
    )
    for q in form_data.questions:
        new_question = Question(
            text=q.text,
            type=q.type,
            options=q.options,
            required=q.required,
        )
        new_form.questions.append(new_question)

    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form

def activate_form(db: Session, form_id: UUID) -> FormType:
    form = db.query(FormType).filter(FormType.id == form_id).first()
    form_addiction_type = db.query(FormType).filter(FormType.id == form_id).first().addiction_type

    active_forms = db.execute(
        select(FormType).filter_by(addiction_type=form_addiction_type, is_active=True)
    )
    for form_old in active_forms.scalars():
        form_old.is_active = False

    if not form:
        raise HTTPException(status_code=401, detail="Invalid form ID")

    form.is_active = True
    db.commit()
    return form


    
