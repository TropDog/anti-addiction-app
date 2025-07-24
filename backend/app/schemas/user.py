from pydantic import BaseModel, EmailStr, constr, field_validator
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    addiction_type: constr(min_length=1)

    @field_validator("password")
    def password_strength(cls, v):
        if len(re.findall(r"\d", v)) < 3:
            raise ValueError("Password must contain at least 3 digits")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "StrongPass123!",
                "addiction_type": "smoking"
            }
        }