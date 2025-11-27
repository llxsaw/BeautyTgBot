from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import set_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(tg_id=message.from_user.id, name=message.from_user.full_name)

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💅 Записаться", callback_data="booking")
    keyboard.button(text="ℹ️ О нас", callback_data="about")

    await message.answer(
        "Привет! Добро пожаловать в наш Салон Красоты.\n"
        "Выберите действие:",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(F.data == "about")
async def about_us(callback: CallbackQuery):
    await callback.message.answer("Мы самый лучший салон в городе! 🌟")
    await callback.answer()
