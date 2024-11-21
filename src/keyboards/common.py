from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.database.enums import UserRole, user_role_to_text


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
