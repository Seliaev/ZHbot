# services/broadcaster.py
import asyncio
import logging
import os
import random
from aiogram import Router
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramForbiddenError

from config import config
from database import db

router = Router()

logger = logging.getLogger(__name__)


def get_random_frog_path():
    """
    Ищет случайную картинку в папке img/frogs.
    Исключает специальный файл NOTWED.jpg.
    Возвращает полный путь к файлу или None, если файлов нет.
    """
    if not os.path.exists(config.FROGS_FOLDER):
        logger.warning(f"Папка {config.FROGS_FOLDER} не найдена!")
        return None

    # Получаем список файлов
    files = []
    for f in os.listdir(config.FROGS_FOLDER):
        # Пропускаем не картинки
        if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            continue

        # ВАЖНО: Исключаем картинку "Не среда", чтобы она не выпала случайно
        if f.lower() == config.NOT_WED_IMG_NAME.lower():
            continue

        files.append(f)

    if not files:
        return None

    return os.path.join(config.FROGS_FOLDER, random.choice(files))


async def broadcast_wednesday(bot: Bot):
    """
    Главная функция рассылки: берет жабу и шлет её всем активным чатам.
    """
    frog_path = get_random_frog_path()
    if not frog_path:
        logger.error("Не найдено ни одной жабы для рассылки! Проверьте папку img/frogs")
        return

    chats = await db.get_active_chats()
    logger.info(f"Начинаю рассылку по {len(chats)} чатам...")

    count = 0
    photo_file = FSInputFile(frog_path)

    for chat_id in chats:
        try:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption="🐸 <b>It is Wednesday, my dudes!</b>",
                parse_mode="HTML"
            )
            count += 1
            # Задержка, чтобы Телеграм не забанил за спам
            await asyncio.sleep(0.056)

        except TelegramForbiddenError:
            # Если бот заблокирован, помечаем чат как неактивный
            logger.info(f"Бот заблокирован в чате {chat_id}. Удаляю из рассылки.")
            await db.remove_chat(chat_id)
        except Exception as e:
            logger.error(f"Ошибка при отправке в {chat_id}: {e}")

    logger.info(f"Рассылка завершена. Успешно: {count} из {len(chats)}")