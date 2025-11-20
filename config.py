# config.py
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()


@dataclass
class Config:
    # Если токена нет, бот не запустится
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")

    # Парсим ID админов из строки "123,456" в список [123, 456]
    ADMIN_IDS: List[int] = field(default_factory=lambda: [
        int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i.strip().isdigit()
    ])

    FROGS_FOLDER: str = os.path.join("img", "frogs")
    DB_PATH: str = os.getenv("DB_PATH", "bot_database.db")

    # Имя специальной картинки для "Не среды" (должна лежать в папке img/frogs/)
    NOT_WED_IMG_NAME: str = "NOTWED.jpg"

    # Тексты сообщений
    MSG_START: str = "👋 <b>Привет!</b> Я жабий бот. Добавь меня в чат, и по средам я буду постить жаб."
    MSG_NOT_WEDNESDAY: str = "🚫 <b>Сегодня не среда, мои чуваки.</b>"
    MSG_NO_FROGS: str = "🐸 Жаб пока нет в папке, но скоро будут!"


config = Config()

if not config.BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")