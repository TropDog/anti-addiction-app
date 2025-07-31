from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from app.core.database import Base

class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    answers = Column(JSONB, nullable=False)

    user = relationship("User")