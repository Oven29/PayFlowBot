from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu
from src.database.enums import UserRole, user_role_to_text, order_bank_to_text


participants_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить участника', callback_data='add-participant-menu')],
    [InlineKeyboardButton(text='Активные участники', callback_data='active-participants')],
    [in_menu_btn],
])


def add_participant(role: UserRole) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=user_role_to_text[UserRole.OPERATOR], callback_data=f'add-participant {UserRole.OPERATOR.value}')],
        [InlineKeyboardButton(text=user_role_to_text[UserRole.PROVIDER], callback_data=f'add-participant {UserRole.PROVIDER.value}')],
    ]

    if role in (UserRole.ADMIN, UserRole.OWNER):
        keyboard.extend([
            [InlineKeyboardButton(text=user_role_to_text[UserRole.ADMIN], callback_data=f'add-participant {UserRole.ADMIN.value}')],
            [InlineKeyboardButton(text=user_role_to_text[UserRole.MANAGER], callback_data=f'add-participant {UserRole.MANAGER.value}')],
        ])

    keyboard.append(
        [InlineKeyboardButton(text='🔙 Назад', callback_data='participants'), in_menu_btn]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def active_participants_menu(role: UserRole) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text='🔍 Поиск по всем пользователям', switch_inline_query_current_chat='participant ')],
        [InlineKeyboardButton(
            text=user_role_to_text[UserRole.OPERATOR],
            switch_inline_query_current_chat=f'participant {UserRole.OPERATOR.value} '),
        ],
        [InlineKeyboardButton(
            text=user_role_to_text[UserRole.PROVIDER],
            switch_inline_query_current_chat=f'participant {UserRole.PROVIDER.value} ')
        ]
    ]

    if role in (UserRole.ADMIN, UserRole.OWNER):
        keyboard.extend([
            [InlineKeyboardButton(
                text=user_role_to_text[UserRole.ADMIN],
                switch_inline_query_current_chat=f'participant {UserRole.ADMIN.value} '),
            ],
            [InlineKeyboardButton(
                text=user_role_to_text[UserRole.MANAGER],
                switch_inline_query_current_chat=f'participant {UserRole.MANAGER.value} ')
            ],
        ])

    keyboard.append(
        [InlineKeyboardButton(text='🔙 Назад', callback_data='participants'), in_menu_btn]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def user_el(user_pk: int, role: int) -> InlineKeyboardMarkup:
    keyboard = []

    if role in (UserRole.OPERATOR, UserRole.PROVIDER):
        keyboard.extend([
            [InlineKeyboardButton(
                text=f'Изменить комиссию {text}',
                callback_data=f'edit-participant-commission {bank.value} {user_pk}',
            )]
              for bank, text in order_bank_to_text.items()
        ])
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
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'active-participants'), in_menu_btn],
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def back_to_participant(user_pk: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'participant-menu {user_pk}'), in_menu_btn],
    ])
