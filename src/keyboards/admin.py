from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu
from .participants import participants_menu
from src.database.enums import UserRole, user_role_to_text


def confirm_delete_participant(user_pk: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='❗ Да, удалить', callback_data=f'confirm-delete-participant {user_pk}'),
         InlineKeyboardButton(text='Отменить действие', callback_data=f'active-participant')],
    ])
