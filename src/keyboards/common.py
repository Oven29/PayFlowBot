from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_btn = InlineKeyboardButton('❌ Отмена', callback_data='cancel')
cancel = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])

back_btn = InlineKeyboardButton('🔙 Назад', callback_data='main-menu')
back = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])

operator_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='', callback_data='')],
])

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='', callback_data='')],
])

provider_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='', callback_data='')],
])
