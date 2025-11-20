# main.py
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import db
from handlers import router as main_router
from services.scheduler import setup_scheduler

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting ZHbot v2.0...")

    # 1. Инициализация БД
    await db.init_db()

    # 2. Настройка бота
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Роутеры
    dp.include_router(main_router)

    # 4. Планировщик
    scheduler = setup_scheduler(bot)
    scheduler.start()

    # 5. Запуск
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        # Корректное завершение
        await bot.session.close()
        logger.info("Bot session closed.")


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped manually.")