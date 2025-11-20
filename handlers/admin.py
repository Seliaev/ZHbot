# handlers/admin.py
import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, PhotoSize
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import config
from database import db
from handlers.cleaner import safe_delete_message, safe_edit_text
from services.broadcaster import broadcast_wednesday

router = Router()


# --- FSM: Состояния для загрузки фото ---
class AdminStates(StatesGroup):
    waiting_for_photo = State()


# --- Вспомогательные функции ---
def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


# --- Хэндлеры ---

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Главное меню админа."""
    if not is_admin(message.from_user.id):
        return

    await safe_delete_message(message)

    stats = await db.get_stats()
    text = (
        f"🕵️‍♂️ <b>Panel admin</b>\n\n"
        f"📊 Активных чатов: <b>{stats['active']}</b>\n"
        f"💀 Мертвых душ: <b>{stats['inactive']}</b>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Загрузить новую жабу", callback_data="admin_upload")],
        [InlineKeyboardButton(text="🚀 Запустить рассылку", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")]
    ])

    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Сбрасываем состояние на всякий случай
    await safe_delete_message(callback.message)


# --- Логика рассылки ---
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_trigger(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    await callback.answer("Рассылка инициирована.")
    await safe_edit_text(callback.message, text="⏳ Выполняется рассылка...", reply_markup=None)

    count = await broadcast_wednesday(callback.bot)

    await callback.message.answer(f"✅ <b>Рассылка завершена!</b>\nДоставлено в {count} чатов.", parse_mode="HTML")


# --- Логика загрузки фото (FSM) ---

@router.callback_query(F.data == "admin_upload")
async def admin_upload_start(callback: CallbackQuery, state: FSMContext):
    """Начало сценария загрузки фото."""
    if not is_admin(callback.from_user.id):
        return

    await callback.answer()
    await callback.message.answer("📸 <b>Отправь мне фото жабы</b>, и я сохраню её в базу.", parse_mode="HTML")
    # Устанавливаем состояние
    await state.set_state(AdminStates.waiting_for_photo)


@router.message(AdminStates.waiting_for_photo, F.photo)
async def admin_upload_process(message: Message, state: FSMContext, bot: Bot):
    """Получение фото и сохранение."""
    try:
        # Берем фото наилучшего качества (последнее в массиве)
        photo: PhotoSize = message.photo[-1]

        # Генерируем имя файла
        file_id = photo.file_id
        file_name = f"{file_id}.jpg"
        destination = os.path.join(config.FROGS_FOLDER, file_name)

        # Скачиваем файл (метод download встроен в aiogram 3)
        await bot.download(photo, destination=destination)

        await message.answer("✅ <b>Фото сохранено!</b> Теперь оно может попасть в рассылку.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}", parse_mode="HTML")
    finally:
        # Завершаем сценарий
        await state.clear()


@router.message(AdminStates.waiting_for_photo)
async def admin_upload_invalid(message: Message):
    """Если админ прислал не фото."""
    await message.answer("⚠️ Это не фото. Пожалуйста, отправь картинку или нажми /cancel (если бы она была).")