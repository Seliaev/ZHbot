# handlers/frog.py
import os
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from services.broadcaster import get_random_frog_path
from handlers.cleaner import safe_delete_message, safe_edit_text
from config import config

router = Router()


@router.callback_query(F.data == "get_frog")
async def callback_frog(callback: CallbackQuery):
    # 0 = Пн, 1 = Вт, 2 = Ср ... 6 = Вс
    is_wednesday = datetime.now().weekday() == 2

    if is_wednesday:
        frog_path = get_random_frog_path()

        if frog_path:
            await safe_delete_message(callback.message)
            photo = FSInputFile(frog_path)
            await callback.message.answer_photo(
                photo=photo,
                caption="🐸 <b>It is Wednesday, my dudes!</b>",
                parse_mode="HTML",
            )
            await callback.answer()
        else:
            await safe_edit_text(
                callback.message,
                text=config.MSG_NO_FROGS,
                reply_markup=None
            )
    else:
        # СЕГОДНЯ НЕ СРЕДА
        # Проверяем, есть ли специальная картинка NOTWED.jpg
        not_wed_path = os.path.join(config.FROGS_FOLDER, config.NOT_WED_IMG_NAME)

        if os.path.exists(not_wed_path):
            # Если картинка есть - удаляем меню и шлем фото
            await safe_delete_message(callback.message)
            photo = FSInputFile(not_wed_path)
            await callback.message.answer_photo(
                photo=photo,
                caption=config.MSG_NOT_WEDNESDAY,
                parse_mode="HTML"

            )
            await callback.answer()
        else:
            # Если картинки нет - просто редактируем текст (как раньше)
            await callback.answer("Сегодня не среда!", show_alert=True)
            await safe_edit_text(
                callback.message,
                text=config.MSG_NOT_WEDNESDAY,
                reply_markup=None
            )