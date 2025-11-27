from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.requests import add_service, add_master

router = Router()


class AddService(StatesGroup):
    name = State()
    price = State()
    duration = State()


@router.message(Command("new_service"))
async def start_add_service(message: Message, state: FSMContext):
    await state.set_state(AddService.name)
    await message.answer("Введите название услуги (например, 'Мужская стрижка'):")


@router.message(AddService.name)
async def add_service_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddService.price)
    await message.answer("Введите цену (число, например: 1500):")


@router.message(AddService.price)
async def add_service_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return

    await state.update_data(price=price)
    await state.set_state(AddService.duration)
    await message.answer("Введите длительность в минутах (целое число, например: 60):")


@router.message(AddService.duration)
async def add_service_duration(message: Message, state: FSMContext):
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Длительность должна быть целым числом.")
        return

    data = await state.get_data()

    await add_service(name=data['name'], price=data['price'], duration=duration)
    await state.clear()
    await message.answer(f"✅ Услуга '{data['name']}' успешно добавлена!")


class AddMaster(StatesGroup):
    name = State()
    info = State()


@router.message(Command("new_master"))
async def start_add_master(message: Message, state: FSMContext):
    await state.set_state(AddMaster.name)
    await message.answer("Введите имя мастера:")\



@router.message(AddMaster.name)
async def add_master_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddMaster.info)
    await message.answer("Введите краткую информацию о мастере (специализация):")


@router.message(AddMaster.info)
async def add_master_info(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_master(name=data['name'], info=message.text)
    await state.clear()
    await message.answer(f"✅ Мастер {data['name']} успешно добавлен!")



