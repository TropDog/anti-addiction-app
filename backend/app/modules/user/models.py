import uuid
import enum
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class QuitStrategy(enum.Enum):
    IMMEDIATELY = "immediately"           
    GRADUAL_REDUCTION = "gradual_reduction"  
    MEDICATION = "medication"             
    BEHAVIORAL_THERAPY = "behavioral_therapy"  
    COMBINATION = "combination"           
    UNDECIDED = "undecided"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    addiction_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    failed_attempts = Column(Integer, default=0, nullable = False)
    blocked_until = Column(DateTime, nullable=True)

    form = relationship("UserProfile")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    nickname = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    tried_quitting = Column(Boolean, nullable=False)
    quitting_reason = Column(String, nullable=False)
    quitting_strategy = Column(
    SAEnum(
        QuitStrategy,
        name="quitstrategy",
        values_callable=lambda enum_cls: [e.value for e in enum_cls], 
        create_type=False
    ),
    nullable=False,
    default=QuitStrategy.UNDECIDED.value
)
    determination_scale =  Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint('determination_scale >= 1 AND determination_scale <= 10', name='determination_scale_range'),
    )