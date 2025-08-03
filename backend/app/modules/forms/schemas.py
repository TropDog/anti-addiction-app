from pydantic import BaseModel
from typing import Dict, Any, Optional
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