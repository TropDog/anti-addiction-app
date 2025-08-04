from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from uuid import UUID

class AnswerSchema(BaseModel):
    answers: Dict[str, Any]

class FormSchema(BaseModel):
    id: UUID
    addiction_type: str
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    text: str
    type: str
    options: Optional[dict] = None
    required: Optional[bool] = True

class FormCreate(BaseModel):
    addiction_type: str
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    questions: List[QuestionCreate] = []