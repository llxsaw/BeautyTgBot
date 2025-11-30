from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import set_user, get_services, get_masters, create_appointment, get_user_appointments
from keyboards.builder import create_buttons


class Booking(StatesGroup):
    service = State()
    master = State()
    date = State()


router = Router()


# --- ГЛАВНОЕ МЕНЮ ---
@router.message(CommandStart())
async def cmd_start(message: Message):
    # Пытаемся сохранить юзера, но если не выйдет - не страшно, create_appointment подстрахует
    await set_user(tg_id=message.from_user.id, name=message.from_user.full_name)

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💅 Записаться", callback_data="booking")
    keyboard.button(text="📅 Мои записи", callback_data="my_appointments")
    keyboard.button(text="ℹ️ О нас", callback_data="about")

    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data == "to_main")
async def back_to_main(callback: CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💅 Записаться", callback_data="booking")
    keyboard.button(text="📅 Мои записи", callback_data="my_appointments")
    keyboard.button(text="ℹ️ О нас", callback_data="about")

    await callback.message.edit_text("Главное меню:", reply_markup=keyboard.adjust(1).as_markup())


# --- ПРОСМОТР ЗАПИСЕЙ ---
@router.callback_query(F.data == "my_appointments")
async def my_appointments(callback: CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔙 Назад", callback_data="to_main")

    appointments = await get_user_appointments(callback.from_user.id)

    if not appointments:
        await callback.message.edit_text(
            "У вас нет активных записей 😔",
            reply_markup=keyboard.as_markup()  # Теперь кнопка точно передается
        )
        return

    text = "📋 **Ваши записи:**\n\n"
    for app in appointments:
        date_str = app.datetime.strftime("%d.%m в %H:%M")
        text += (f"🔹 **Услуга:** {app.service.name}\n"
                 f"👤 **Мастер:** {app.master.name}\n"
                 f"🕒 **Время:** {date_str}\n"
                 f"➖➖➖➖➖➖➖➖\n")

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")


# --- СЦЕНАРИЙ ЗАПИСИ ---
@router.callback_query(F.data == "booking")
async def select_service(callback: CallbackQuery, state: FSMContext):
    services = await get_services()
    if not services:
        await callback.answer("Услуг пока нет 😢")
        return
    keyboard = create_buttons(services, "service")
    await callback.message.edit_text("Выберите услугу:", reply_markup=keyboard)
    await state.set_state(Booking.service)


@router.callback_query(F.data.startswith("service_"))
async def select_master(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)

    masters = await get_masters()
    keyboard = create_buttons(masters, "master")
    await callback.message.edit_text("Выберите мастера:", reply_markup=keyboard)
    await state.set_state(Booking.master)
    await callback.answer()


@router.callback_query(F.data.startswith("master_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    master_id = int(callback.data.split("_")[1])
    await state.update_data(master_id=master_id)

    await callback.message.edit_text("Напишите дату и время (пример: 12.10 14:00):")
    await state.set_state(Booking.date)
    await callback.answer()


@router.message(Booking.date)
async def finalize_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    date_text = message.text

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="В меню", callback_data="to_main")

    try:
        await create_appointment(
            tg_id=message.from_user.id,
            service_id=data['service_id'],
            master_id=data['master_id'],
            datetime_str=date_text
        )
        await message.answer("✅ Запись успешно создана!", reply_markup=keyboard.as_markup())
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Ошибка даты! Формат: ДД.ММ ЧЧ:ММ (пример: 12.10 14:00)")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")