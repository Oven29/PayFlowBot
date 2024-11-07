from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_btn = InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')
cancel = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])

in_menu_btn = InlineKeyboardButton(text='🔝 В меню', callback_data='main-menu')
in_menu = InlineKeyboardMarkup(inline_keyboard=[[in_menu_btn]])

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Участники', callback_data='admin participants')],
    [InlineKeyboardButton(text='Заявки', callback_data='admin orders')],
])

operator_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='', callback_data='')],
])

provider_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='', callback_data='')],
])
