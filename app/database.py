import asyncpg
from typing import Optional
import os


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Создание пула соединений с БД"""
        self.pool = await asyncpg.create_pool(
            os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:postgres@localhost:5434/students_db",
            ),
            min_size=5,
            max_size=20,
        )

    async def disconnect(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        """Выполнение SQL запроса без возврата данных"""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Выполнение SQL запроса с возвратом всех строк"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Выполнение SQL запроса с возвратом одной строки"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def executemany(self, query: str, args_list):
        """Выполнение множественных запросов"""
        async with self.pool.acquire() as connection:
            return await connection.executemany(query, args_list)


db = Database()
