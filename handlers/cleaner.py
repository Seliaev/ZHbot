import logging
from contextlib import suppress
from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

async def safe_delete_message(message: Message):
    """
    Безопасное удаление сообщения.
    Игнорирует ошибки, если сообщение уже удалено или его нельзя удалить.
    """
    with suppress(TelegramBadRequest):
        await message.delete()

async def safe_edit_text(message: Message, text: str, reply_markup=None):
    """
    Безопасное изменение текста сообщения.
    """
    with suppress(TelegramBadRequest):
        await message.edit_text(text=text, reply_markup=reply_markup, parse_mode="HTML")