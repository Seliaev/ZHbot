# services/__init__.py
from aiogram import Router
from . import broadcaster, scheduler

# Создаем главный роутер
router = Router()

# Подключаем все остальные файлы с хэндлерами
router.include_router(broadcaster.router)
router.include_router(scheduler.router)