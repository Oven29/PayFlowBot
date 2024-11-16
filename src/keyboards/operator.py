from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel, cancel_btn
from src.database.enums import order_bank_to_text


in_menu_btn = InlineKeyboardButton(text='🔝 В меню', callback_data='operator-menu')
in_menu = InlineKeyboardMarkup(inline_keyboard=[[in_menu_btn]])

select_bank = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=text, callback_data=f'select-bank {bank.value}')]
      for bank, text in order_bank_to_text.items()
] + [
    [in_menu_btn],
])


confirm_adding_order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Да, добавить', callback_data='confirm-add-order')],
    [InlineKeyboardButton(text='🔁 Заполнить заново', callback_data='add-order')],
])
