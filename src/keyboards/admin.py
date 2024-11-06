from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu
from src.database.enums import order_status_to_text


orders_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=text, switch_inline_query_current_chat=f'order {status.value} ')]
    for status, text in order_status_to_text.items()
] + [in_menu_btn])

order_el = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Назад', callback_data=f'admin participants')],
    in_menu_btn,
])
