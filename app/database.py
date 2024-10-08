import asyncpg
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user='al_services',
            password='AlohbaiN4beeghoozechaig1',
            database='al_services',
            host='db'
        )

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *args)
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {str(e)}")
            raise

    async def fetchval(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchval(query, *args)
        except Exception as e:
            logger.error(f"Ошибка получения значения: {str(e)}")
            raise

# import asyncpg
# import os
# import logging
#
# logger = logging.getLogger(__name__)
#
# class Database:
#     def __init__(self):
#         self.db_host = os.getenv("DB_HOST", "192.168.2.50")
#         self.db_port = os.getenv("DB_PORT", "5432")
#         self.db_name = os.getenv("DB_NAME", "al_services")
#         self.db_user = os.getenv("DB_USER", "al_services")
#         self.db_password = os.getenv("DB_PASSWORD", "AlohbaiN4beeghoozechaig1")
#         self.pool = None
#
#     async def connect(self):
#         try:
#             self.pool = await asyncpg.create_pool(
#                 host=self.db_host,
#                 port=self.db_port,
#                 user=self.db_user,
#                 password=self.db_password,
#                 database=self.db_name,
#             )
#             logger.info("Подключение к базе данных успешно")
#         except Exception as e:
#             logger.error(f"Ошибка подключения к базе данных: {str(e)}")
#
#     async def close(self):
#         if self.pool:
#             await self.pool.close()
#             logger.info("Соединение с базой данных закрыто")
#
#     async def execute(self, query, *args):
#         try:
#             async with self.pool.acquire() as connection:
#                 return await connection.execute(query, *args)
#         except Exception as e:
#             logger.error(f"Ошибка выполнения запроса: {str(e)}")
#
#     async def fetch(self, query, *args):
#         try:
#             async with self.pool.acquire() as connection:
#                 return await connection.fetch(query, *args)
#         except Exception as e:
#             logger.error(f"Ошибка получения данных: {str(e)}")
#
#
#
