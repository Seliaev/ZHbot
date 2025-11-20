# database.py
import aiosqlite
import logging
from config import config

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.db_path = config.DB_PATH

    async def init_db(self):
        """Инициализация таблиц базы данных."""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица чатов: хранит ID чата, тип и статус активности
            await db.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    chat_type TEXT,
                    active INTEGER DEFAULT 1,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
            logger.info("База данных инициализирована.")

    async def add_chat(self, chat_id: int, chat_type: str):
        """Добавление нового чата или повторная активация старого."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO chats (chat_id, chat_type, active) VALUES (?, ?, 1)",
                (chat_id, chat_type)
            )
            await db.execute("UPDATE chats SET active = 1 WHERE chat_id = ?", (chat_id,))
            await db.commit()

    async def remove_chat(self, chat_id: int):
        """Мягкое удаление (помечаем как неактивный, чтобы не слать спам)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE chats SET active = 0 WHERE chat_id = ?", (chat_id,))
            await db.commit()

    async def get_active_chats(self):
        """Получить список ID всех активных чатов для рассылки."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT chat_id FROM chats WHERE active = 1") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def get_stats(self):
        """Статистика для админки."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM chats WHERE active = 1") as cursor:
                active = await cursor.fetchone()

            async with db.execute("SELECT COUNT(*) FROM chats WHERE active = 0") as cursor:
                inactive = await cursor.fetchone()

        return {
            "active": active[0] if active else 0,
            "inactive": inactive[0] if inactive else 0
        }


db = Database()