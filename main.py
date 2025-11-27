import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database.models import Base

from handlers.admin import router as admin_router
from handlers.user import router as user_router

load_dotenv()

# Setting and connect PostgreSQL
# echo=True будет выводить все SQL-запросы в консоль (удобно для отладки)
engine = create_async_engine(url=os.getenv('DB_URL'), echo=True)

# Фабрика сессий (через неё мы будем делать запросы)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def main():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ База данных подключена и таблицы созданы!")

    # 2. Запуск бота
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()

    dp.include_router(admin_router)
    dp.include_router(user_router)

    print("🤖 Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('⛔ Бот остановлен')