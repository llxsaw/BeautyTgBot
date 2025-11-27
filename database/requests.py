from database.models import Service, Master, User
from database.models import async_sessionmaker
from sqlalchemy import select


async def add_service(name: str, price: float, duration: int):
    async with async_sessionmaker() as session:
        service = Service(name=name, price=price, duration=duration)
        session.add(service)
        await session.commit()


async def get_services():
    async with async_sessionmaker() as session:
        result = await session.execute(select(Service))
        return result.scalars().all()


async def add_master(name: str, info: str):
    async with async_sessionmaker() as session:
        master = Master(name=name, info=info)
        session.add(master)
        await session.commit()


async def set_user(tg_id: int, name: str):
    async with async_sessionmaker() as session:
        user = await session.scalars(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()
