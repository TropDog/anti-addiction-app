import uuid
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import Session
from app.modules.user.models import UserProfile
from app.modules.gpt_module.models import Chat, Message, ConversationState

def prepare_intro_context(user_profile, chat):
    return {
        "chat": {
            "id": str(chat.id),
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "updated_at": chat.updated_at.isoformat(),
        },
        "user_profile": {
            "nickname": user_profile.nickname,
            "age": user_profile.age,
            "tried_quitting": user_profile.tried_quitting,
            "quitting_reason": user_profile.quitting_reason,
            "quitting_strategy": user_profile.quitting_strategy.value,
            "determination_scale": user_profile.determination_scale,
            "created_at": user_profile.created_at.isoformat(),
        },
        "intro_message": (
            "Hello! This is your first chat."
            "Based on your information, I will try to help you as best I can."
            "Tell me about your expectations."
        ),
        "messages": []
    }


def prepare_full_context(chat, user_profile, conversation_state, messages):
    return {
        "chat": {
            "id": str(chat.id),
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "updated_at": chat.updated_at.isoformat(),
        },
        "user_profile": {
            "nickname": user_profile.nickname,
            "age": user_profile.age,
            "tried_quitting": user_profile.tried_quitting,
            "quitting_reason": user_profile.quitting_reason,
            "quitting_strategy": user_profile.quitting_strategy.value,
            "determination_scale": user_profile.determination_scale,
            "created_at": user_profile.created_at.isoformat(),
        },
        "conversation_state": {
            "summary": conversation_state.summary if conversation_state else None,
            "updated_at": conversation_state.updated_at.isoformat() if conversation_state else None,
        },
        "messages": [
            {
                "sender": msg.sender.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            } for msg in messages
        ]
    }


def get_chat_context(session: Session, chat_id: uuid.UUID, last_messages_limit: int = 10):
    chat = session.execute(select(Chat).where(Chat.id == chat_id)).scalar_one_or_none()
    if not chat:
        raise Exception("Chat not found")  

    user_profile = session.execute(
        select(UserProfile).where(UserProfile.user_id == chat.user_id)
    ).scalar_one_or_none()

    if not user_profile:
        return None  

    user_chats = session.execute(
        select(Chat).where(Chat.user_id == chat.user_id)
    ).scalars().all()

    if len(user_chats) == 1:
        return prepare_intro_context(user_profile, chat), True

    conversation_state = session.execute(
        select(ConversationState).where(ConversationState.chat_id == chat_id)
    ).scalar_one_or_none()

    messages = session.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(desc(Message.created_at))
        .limit(last_messages_limit)
    ).scalars().all()

    messages.reverse()

    return prepare_full_context(chat, user_profile, conversation_state, messages), False

def prepare_system_content(context: dict, is_first_chat: bool) -> str:
    user = context.get("user_profile", {})
    summary = context.get("summary", "")
    chat_title = context.get("chat_title", "Therapy Chat")
    
    nickname = user.get("nickname", "User")
    age = user.get("age", "unknown age")
    tried_quitting = user.get("tried_quitting", False)
    quitting_reason = user.get("quitting_reason", "unspecified reasons")
    quitting_strategy = user.get("quitting_strategy", "undecided")
    determination_scale = user.get("determination_scale", "unknown")
    
    if is_first_chat:
        intro = (
            f"Welcome! You are about to engage in a private, personalized therapy session with an personal therapist. "
            f"This session is designed to support {nickname}, a {age}-year-old individual, "
            f"who is voluntarily seeking help with addiction-related challenges. "
            f"{nickname} has {'attempted quitting before' if tried_quitting else 'not tried quitting before'}, "
            f"with reasons related to {quitting_reason}. Their current quitting strategy is '{quitting_strategy}', "
            f"and their determination to quit is rated at {determination_scale} out of 10.\n\n"
            "Your role is to empathize deeply, adapt to the user's emotional state, and provide thoughtful, supportive guidance. "
            "Remember, this is a voluntary therapeutic setting focused on harm reduction and personalized assistance.\n"
            "Please engage gently, validate feelings, and avoid judgment.\n\n"
            "Below is the initial context and goals for this therapy session."
        )
    else:
        intro = (
            f"This is a continuation of a therapy session titled '{chat_title}'. "
            f"You are supporting {nickname}, a {age}-year-old individual working on addiction recovery.\n\n"
            "Use the following summary of past conversations to understand their current state:\n"
            f"{summary}\n\n"
            "Maintain empathy and adapt your responses to the user's ongoing emotional and motivational state. "
            "Your goal is to provide personalized, compassionate therapeutic support aligned with the user's profile and history."
        )
    
    requirements = (
        "\n\nPlease always:\n"
        "- You are a compassionate and skilled therapist helping the user through their struggles\n"
        "- Embody the role of a compassionate, non-judgmental therapist.\n"
        "- Your responses should be warm, empathetic, and insightful, just like a real therapist would give."
        "- Use evidence-based motivational techniques when appropriate.\n"
        "- Avoid giving direct medical advice or diagnosis.\n"
        "- Focus on understanding the user's feelings and providing thoughtful guidance.\n"
        "- Encourage voluntary progress and respect user's pace.\n"
        "- Make sure to consider the user's quitting strategy and determination level.\n"
        "- Use clear, supportive language, and validate user emotions."
        "- Do not mention that you are an AI."
    )
    
    return intro + requirements
