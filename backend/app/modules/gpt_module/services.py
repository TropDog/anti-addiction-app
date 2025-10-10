import uuid
from sqlalchemy import select, desc, asc, func
from sqlalchemy.orm import Session
from app.modules.user.models import UserProfile, User
from app.modules.gpt_module.models import Chat, Message, ConversationState, SenderEnum
from openai import OpenAI
from fastapi import WebSocket
from dotenv import load_dotenv
import os
import logging
import asyncio

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_SECRET_KEY"))
logger = logging.getLogger("uvicorn")


THERAPIST_BEHAVIOR_PROMPT = """
You are an empathetic therapist supporting individuals struggling with addiction.
Your goal is not only to show understanding, but also to help the user reflect on their behavior, emotions, and underlying causes of addiction.
Use compassionate and natural language, but also guide the conversation so that the user:
- can explore the sources of their emotions and motivation,
- can find practical steps they can take,
- feels that the conversation is evolving rather than repeating.

Avoid repeating generic phrases such as "I'm here for you" or "How are you feeling?".
If the user has already expressed their emotions, acknowledge them and gently propose a direction for reflection or the next step in the conversation.
"""

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
        select(UserProfile)
        .where(UserProfile.user_id == chat.user_id)
        .order_by(UserProfile.created_at.desc()) 
    ).scalars().first()

    if not user_profile:
        return None  

    user_chats = session.execute(
        select(Chat).where(Chat.user_id == chat.user_id)
    ).scalars().all()

    if not chat.messages or len(chat.messages) == 0:
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
    conversation_state = context.get("conversation_state", {})
    summary = conversation_state.get("summary", "")
    chat_title = context.get("chat", {}).get("title", "Therapy Chat")
    
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
    
    return intro + requirements + "\n\n" + THERAPIST_BEHAVIOR_PROMPT

def creat_new_chat(user: User, chat_title: str, db: Session):
    new_chat = Chat(
        user_id = user.id,
        title = chat_title
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

def save_message(chat_id: uuid.UUID, db: Session, data, sender: SenderEnum):
    user_msg = Message(
        chat_id=chat_id,
        sender=sender,
        content=data,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

async def run_in_thread(func, *args, **kwargs):
    return await (asyncio.to_thread(func, *args, **kwargs))

def update_conversation_state(db: Session, chat: Chat, last_messages: list[Message]):
    previous_summary = chat.conversation_state.summary if chat.conversation_state else "No summary yet."

    messages_text = "\n".join([
        f"{msg.sender.value}: {msg.content}" for msg in last_messages
    ])

    summarization_prompt = [
        {"role": "system", "content": "You are a summarizer of therapy chat sessions. Summarize in neutral, factual, empathetic style."},
        {"role": "user", "content": f"Previous summary:\n{previous_summary}"},
        {"role": "user", "content": f"Recent messages:\n{messages_text}"},
        {"role": "user", "content": "Update the summary to reflect the current state of the conversation. Keep it concise (max 5 sentences)."}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=summarization_prompt,
        temperature=0.3,
    )
    new_summary = response.choices[0].message.content.strip()

    if not chat.conversation_state:
        chat.conversation_state = ConversationState(
            chat_id=chat.id,
            summary=new_summary
        )
    else:
        chat.conversation_state.summary = new_summary

    db.add(chat)
    db.commit()
    db.refresh(chat.conversation_state)

    return chat.conversation_state

async def handle_chat_logic(
    websocket: WebSocket,
    db: Session,
    chat_id: uuid.UUID
):
    """
    Websocket chat logic.
    - saves every msg into db
    - creates context
    - after every 10 new messages creates new summary
    """

    await websocket.accept()
    logger.info("WebSocket accepted, now entering receive loop")
    try:
        while True:
            user_message = await websocket.receive_text()
            logger.debug(f"Received message: {user_message}")
            await websocket.send_text(f"Echo: {user_message}")

            chat = await run_in_thread(
                lambda: db.execute(select(Chat).where(Chat.id == chat_id)).scalar_one()
            )

            logger.info(f"Loaded chat from DB: {chat.id}")

            await run_in_thread(save_message, chat_id, db, user_message, SenderEnum.user.value)
            logger.info(f"Saved user message to DB: {user_message}")
            context, is_first_chat = await run_in_thread(
                get_chat_context, db, chat.id, last_messages_limit=10
            )
            system_prompt = str(prepare_system_content(context, is_first_chat))
            logger.debug(f"Prepared system prompt: {system_prompt[:50]}...")

            history_messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            for msg in context["messages"]:
                history_messages.append({
                    "role": "user" if msg["sender"] == "user" else "assistant",
                    "content": msg["content"]
                })
            
            history_messages.append({
                "role": "user",
                "content": user_message
            })            

            if not any(msg["content"] == user_message for msg in context["messages"]):
                context["messages"].append({
                    "sender": "user",
                    "content": user_message,
                    "created_at": "now"  
                })

            logger.debug(f"History messages prepared: {len(history_messages)} messages")

            response = await run_in_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=history_messages,
                temperature=0.7,
                max_tokens=400,
            )

            ai_message = response.choices[0].message.content.strip()
            logger.info(f"Received AI message: {ai_message[:50]}...")

            await run_in_thread(save_message, chat_id, db, ai_message, SenderEnum.therapist.value)
            logger.info("Saved AI message to DB")

            await websocket.send_text(str(ai_message))

            total_messages = await run_in_thread(
                lambda: db.execute(
                    select(func.count(Message.id)).where(Message.chat_id == chat.id)
                ).scalar()  
            )

            logger.debug(f"Total messages in chat: {total_messages}")

            if total_messages % 10 == 0:
                last_messages = await run_in_thread(
                    lambda: db.execute(
                        select(Message)
                        .where(Message.chat_id == chat.id)
                        .order_by(desc(Message.created_at))
                        .limit(10)
                    ).scalars().all()
                )
                last_messages.reverse()
            
                await run_in_thread(update_conversation_state, db, chat, last_messages)
                logger.info("Chat summary updated and sent to WebSocket")

    except Exception as e:
        logger.exception("Unexpected error in websocket")
        try:
            reason = str(e)[:100]
            await websocket.close(code=1011, reason=reason)
        except RuntimeError:
            pass