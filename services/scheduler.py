# services/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram import Router
from services.broadcaster import broadcast_wednesday

router = Router()

def setup_scheduler(bot: Bot):
    """
    Настройка расписания.
    """
    # Используем Московское время
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # Задача: Запускать broadcast_wednesday каждую среду (wed) в 12:00
    scheduler.add_job(
        broadcast_wednesday,
        trigger='cron',
        day_of_week='wed',
        hour=12,
        minute=0,
        kwargs={'bot': bot} # Передаем бота внутрь функции
    )

    return scheduler