# handlers/events.py
import logging
from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER, ADMINISTRATOR, RESTRICTED
from database import db

router = Router()
logger = logging.getLogger(__name__)

# Когда бота добавляют в группу или личку
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER | ADMINISTRATOR | RESTRICTED))
async def on_bot_added(event: ChatMemberUpdated):
    chat_type = event.chat.type
    if chat_type in ["group", "supergroup", "private"]:
        await db.add_chat(event.chat.id, chat_type)
        logger.info(f"Новый чат: {event.chat.id} ({event.chat.title or 'ЛС'})")

# Когда бота удаляют/блокируют
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def on_bot_removed(event: ChatMemberUpdated):
    await db.remove_chat(event.chat.id)
    logger.info(f"Бот удален из чата: {event.chat.id}")