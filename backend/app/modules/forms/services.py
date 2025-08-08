from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.modules.forms.models import FormType, Question, Answer
from app.modules.user.models import UserProfile, QuitStrategy
from app.modules.forms.schemas import FormCreate
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime

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
            user_profile_field_name = q.user_profile_field_name,
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

def update_user_profile_from_answers(db: Session, user_id: UUID, form_id: UUID):
    questions_with_fields = db.query(Question).filter(
        Question.form_id == form_id,
        Question.user_profile_field_name.isnot(None)
    ).all()

    question_field_map = {q.id: q.user_profile_field_name for q in questions_with_fields}

    user_answers = db.query(Answer).filter(
        Answer.form_id == form_id,
        Answer.user_id == user_id,
        Answer.question_id.in_(question_field_map.keys())
    ).all()
    print("AAAAAAAAAAA!@!@#!@#!#!#!#!AAAAAAAAAAAAAAAAAAa")
    print(f"Question field map: {question_field_map}")
    print(f"User answers: {[ (a.question_id, a.value) for a in user_answers ]}")

    profile_data = {
        "user_id": user_id,
        "nickname": "no nickname",
        "age": 0,
        "tried_quitting": False,
        "quitting_reason": "undefined",
        "quitting_strategy": QuitStrategy.UNDECIDED.value,
        "determination_scale": 1,
        "created_at": datetime.utcnow()
    }

    for answer in user_answers:
        field = question_field_map.get(answer.question_id)
        if not field:
            continue

        value = answer.value

        if field == "quitting_strategy":
            try:
                value = QuitStrategy(value).value
            except ValueError:
                continue

        if field in ["age", "determination_scale"]:
            try:
                value = int(value)
            except (TypeError, ValueError):
                continue

        if field == "tried_quitting":
            value = bool(value)

        profile_data[field] = value

    profile = UserProfile(**profile_data)

    db.add(profile)
    db.commit()
