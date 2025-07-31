from pydantic import BaseModel
from typing import Dict, Any

class FormSubmitRequest(BaseModel):
    answers: Dict[str, Any]

class FormResponse(BaseModel):
    message: str