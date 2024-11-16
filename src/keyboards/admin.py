from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel
from src.database.enums import UserRole, user_role_to_text


in_menu_btn = InlineKeyboardButton(text='🔝 В меню', callback_data='admin-menu')
in_menu = InlineKeyboardMarkup(inline_keyboard=[[in_menu_btn]])

participants_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить участника', callback_data='add-participant-menu')],
    [InlineKeyboardButton(text='Активные участники', callback_data='active-participants')],
    [in_menu_btn],
])

add_participant = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=text, callback_data=f'add-participant {role.value}')]
      for role, text in user_role_to_text.items()
] + [
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin participants'), in_menu_btn],
])

active_participants_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔍 Поиск по всем пользователям', switch_inline_query_current_chat='participant ')],
] + [
    [InlineKeyboardButton(text=text, switch_inline_query_current_chat=f'participant {status.value} ')]
      for status, text in user_role_to_text.items()
] + [
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin participants'), in_menu_btn]
])


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
