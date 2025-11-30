from database.models import Service, Master, User
from database.models import async_sessionmaker
from sqlalchemy import select
from datetime import datetime
from sqlalchemy.orm import joinedload

from database.models import Appointment


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


async def get_masters():
    async with async_sessionmaker() as session:
        result = await session.execute(select(Master))
        return result.scalars().all()


async def set_user(tg_id: int, name: str):
    async with async_sessionmaker() as session:
        user = await session.scalars(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()


async def create_appointment(user_id, service_id, master_id, datetime_str):
    async with async_sessionmaker() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))

        dt = datetime.strptime(datetime_str, "%d.%m %H:%M")

        appointment = Appointment(
            user_id=user.id,
            service_id=service_id,
            master_id=master_id,
            datetime=dt,
        )

        session.add(appointment)
        await session.commit()


async def get_user_appointments(tg_id: int):
    async with async_sessionmaker() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            return []

        result = await session.execute(
            select(Appointment)
            .where(Appointment.user_id == user.id)
            .options(joinedload(Appointment.service), joinedload(Appointment.master))
            .order_by(Appointment.datetime)
        )

        return result.scalars().all()

