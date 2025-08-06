from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.auth import get_current_admin
from app.modules.forms.services import create_form_service, activate_form
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

@router.post("/add_form", tags=["forms-admin"])
def create_form(
    form_data: schemas.FormCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin)
):
    try:
        new_form = create_form_service(db, form_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": new_form.id, "message": "Form created successfully"}

@router.post("/activate_form/{form_id}", tags=["forms-admin"])
def change_active_form(
    form_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin)
):
    try:
        activated_form = activate_form(db, form_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": activated_form.id, "message": "Form activated successfully"}

@router.get("/types/all", tags=["forms-admin"])
def get_all_forms(db: Session = Depends(get_db),
                  user: User = Depends(get_current_admin)
):
    forms = db.query(models.FormType).all()
    return forms