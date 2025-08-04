from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from app.core.database import Base

class FormType(Base):
    __tablename__ = "forms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    addiction_type = Column(String, unique=False, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    questions = relationship("Question", back_populates="form", cascade="all, delete")

class Question(Base):
    __tablename__ = "questions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), ForeignKey("forms.id"), nullable=False)
    text = Column(String, nullable=False)
    type = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    required = Column(Boolean, default=True)

    form = relationship("FormType")

class Answer(Base):
    __tablename__ = "answers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), ForeignKey("forms.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, nullable=False)

    form = relationship("FormType")
    user = relationship("User")
