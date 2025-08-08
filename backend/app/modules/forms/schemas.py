from pydantic import BaseModel
from typing import Optional, List, Union
from uuid import UUID


class QuestionAnswer(BaseModel):
    question_id: UUID
    value: Union[str, int, float, bool, dict, list]

class AnswerSubmitSchema(BaseModel):
    answers: List[QuestionAnswer]

class QuestionCreate(BaseModel):
    text: str
    type: str
    user_profile_field_name: str
    options: Optional[dict] = None
    required: Optional[bool] = True

class FormCreate(BaseModel):
    addiction_type: str
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    questions: List[QuestionCreate] = []