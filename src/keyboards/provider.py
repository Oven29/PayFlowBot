from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel
from src.database.enums import UserProviderStatus


in_menu_btn = InlineKeyboardButton(text='🔝 В меню', callback_data='provider-menu')
in_menu = InlineKeyboardMarkup(inline_keyboard=[[in_menu_btn]])

select_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Тинькофф', callback_data=f'select-status {UserProviderStatus.ACTIVE_TINK.value}')],
    [InlineKeyboardButton(text='МежБанк', callback_data=f'select-status {UserProviderStatus.ACTIVE_INTER.value}')],
    [in_menu_btn],
])


def turn_on_status(status: UserProviderStatus) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Включить', callback_data=f'turn-on-status {status.value}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='start-work'),],
    ])


turn_off_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⛔ Выключить', callback_data=f'turn-off-status')],
])


def accept_order(order_id: int, reject_button: bool = True) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text='✅ Принять', callback_data=f'accept-order {order_id}')],
    ]
    if reject_button:
        keyboard.append([InlineKeyboardButton(text='❌ Отклонить', callback_data=f'reject-order {order_id}')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def finish_order(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Ввести чек', callback_data=f'finish-order {order_id}')],
        [InlineKeyboardButton(text='! Открыть диспут', callback_data=f'create-dispute {order_id}')],
    ])
