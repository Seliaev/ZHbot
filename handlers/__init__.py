# handlers/__init__.py
from aiogram import Router
from . import start, frog, events, admin

# Создаем главный роутер
router = Router()

# Подключаем все остальные файлы с хэндлерами
router.include_router(start.router)
router.include_router(frog.router)
router.include_router(admin.router)
router.include_router(events.router)