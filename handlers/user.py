from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import set_user, get_services, get_masters
from keyboards.builder import create_buttons


class Booking(StatesGroup):
    service = State()
    master = State()
    date = State()


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, name=message.from_user.full_name)

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💅 Записаться", callback_data="booking")
    keyboard.button(text="ℹ️ О нас", callback_data="about")

    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data == "booking")
async def select_service(callback: CallbackQuery, state: FSMContext):
    services = await get_services()

    if not services:
        await callback.answer("Услуг пока нет 😢")
        return

    keyboard = create_buttons(services, 'service')

    await callback.message.edit_text("Выберите услугу:", reply_markup=keyboard)
    await state.set_state(Booking.service)


@router.callback_query(F.data.startswith("service_"))
async def select_master(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])

    await state.update_data(service_id=service_id)

    masters = await get_masters()
    keyboard = create_buttons(masters, 'master')

    await callback.message.edit_text("Отлично! Теперь выберите мастера:", reply_markup=keyboard)
    await state.set_state(Booking.master)

    await callback.answer()


@router.callback_query(F.data.startswith("master_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    master_id = int(callback.data.split("_")[1])
    await state.update_data(master_id=master_id)

    await callback.message.edit_text("Напишите желаемую дату и время (например: 12.10 14:00):")
    await state.set_state(Booking.date)


@router.message(Booking.date)
async def finalize_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    date_text = message.text

    summary = (f"✅ Запись подтверждена!\n\n"
               f"Услуга ID: {data['service_id']}\n"
               f"Мастер ID: {data['master_id']}\n"
               f"Время: {date_text}")

    await message.answer(summary)
    await state.clear()


@router.callback_query()
async def debug_handler(callback: CallbackQuery):
    # Этот хендлер срабатывает, если ни один другой не подошел
    print(f"😱 КНОПКА ОТПРАВИЛА ДАННЫЕ: {callback.data}")
    await callback.answer("Кнопка не обработана, смотри консоль")



