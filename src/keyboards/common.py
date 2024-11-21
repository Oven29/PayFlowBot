from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_btn = InlineKeyboardButton(text='✖️ Отмена', callback_data='cancel')
cancel = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])

in_menu_btn = InlineKeyboardButton(text='🔝 В меню', callback_data='main-menu')
in_menu = InlineKeyboardMarkup(inline_keyboard=[[in_menu_btn]])

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Участники', callback_data='participants')],
    [InlineKeyboardButton(text='Заявки', callback_data='orders')],
])

operator_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить заявку', callback_data='add-order')],
    [InlineKeyboardButton(text='Заявки', callback_data='orders')],
])

provider_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать сессию', callback_data='start-work')],
    [InlineKeyboardButton(text='Диспуты', callback_data='provider-disputes')],
])

manager_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Участники', callback_data='participants')],
])

confirm_remove_account = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❗ Да, удалить', callback_data='confirm-remove-account')],
    [InlineKeyboardButton(text='❌ Отмена', callback_data='main-menu')],
])


def update_order_info(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔁 Обновить информацию', callback_data=f'update-order-info {order_id}')],
    ])
