from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu
from src.database.enums import UserProviderStatus


select_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Тинькофф', callback_data=f'select-status {UserProviderStatus.ACTIVE_TINK.value}')],
    [InlineKeyboardButton(text='МежБанк', callback_data=f'select-status {UserProviderStatus.ACTIVE_INTER.value}')],
    [in_menu_btn],
])


def turn_on_status(status: UserProviderStatus):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Включить', callback_data=f'turn-on-status {status.value}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='start-work'),],
    ])


turn_off_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⛔ Выключить', callback_data=f'turn-off-status')],
])
