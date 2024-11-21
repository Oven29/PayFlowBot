from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu, participants_menu
from src.database.enums import UserRole, user_role_to_text


def user_el(user_pk: int, role: int) -> InlineKeyboardMarkup:
    keyboard = []

    if role in (UserRole.OPERATOR, UserRole.PROVIDER):
        keyboard.append([InlineKeyboardButton(
            text='Изменить комиссию',
            callback_data=f'edit-participant-commission {user_pk}',
        )])
        keyboard.append([InlineKeyboardButton(
            text='Изменить баланс',
            callback_data=f'edit-participant-balance {user_pk}',
        )])
    if role is UserRole.PROVIDER:
        keyboard.append([InlineKeyboardButton(
            text='Выключить провайдера',
            callback_data=f'disable-provider {user_pk}',
        )])

    keyboard.extend([
        [InlineKeyboardButton(text='Удалить', callback_data=f'delete-participant {user_pk}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'active-participant'), in_menu_btn],
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirm_delete_participant(user_pk: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='❗ Да, удалить', callback_data=f'confirm-delete-participant {user_pk}'),
         InlineKeyboardButton(text='Отменить действие', callback_data=f'active-participant')],
    ])
