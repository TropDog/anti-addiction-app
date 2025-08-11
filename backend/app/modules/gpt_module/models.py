import enum
import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Enum, Text, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class SenderEnum(str,enum.Enum):
    user = "user"
    therapist = "therapist"

class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
   
    user = relationship("User")
    messages = relationship("Message", back_populates="chat",cascade="all, delete-orphan")
    conversation_state = relationship("ConversationState", back_populates="chat", uselist=False, cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, unique=True)
    sender = Column(Enum(SenderEnum, name="sender_enum"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chat = relationship("Chat")
    
    __table_args__ = (
Index("idx_messages_chat_created", "chat_id", "created_at")
    )

class ConversationState(Base):
    __tablename__ = "conversation_states"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    chat = relationship("Chat", back_populates="conversation_state")
