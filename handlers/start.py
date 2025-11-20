# handlers/start.py
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from handlers.cleaner import safe_delete_message
from config import config
from database import db

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Сохраняем пользователя в базу данных
    await db.add_chat(message.chat.id, message.chat.type)

    # Удаляем команду /start, чтобы не мусорить
    await safe_delete_message(message)

    # Кнопка
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐸 Хочу жабу!", callback_data="get_frog")]
    ])

    # Ответ бота
    await message.answer(
        text=config.MSG_START,
        reply_markup=kb,
        parse_mode="HTML"
    )