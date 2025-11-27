from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_buttons(items, prefix):
    keyboard = InlineKeyboardBuilder()

    for item in items:
        keyboard.button(text=item.name, callback_data=f"{prefix}_{item.id}")

    return keyboard.adjust(1).as_markup()
