from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu
from src.database.enums import OrderStatus, UserRole, order_status_to_text, user_role_to_text


orders_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔍 Поиск по всем заявкам', switch_inline_query_current_chat='order ')],
] + [
    [InlineKeyboardButton(text=text, switch_inline_query_current_chat=f'order {status.value} ')]
      for status, text in order_status_to_text.items()
] + [
    [InlineKeyboardButton(text='🔙 Назад', callback_data='main-menu')],
])


def order_el(order_id: int, status: OrderStatus) -> InlineKeyboardMarkup:
    keyboard = []

    if isinstance(status, OrderStatus.CANCELLED):
        keyboard.append([InlineKeyboardButton(
            text='Перенести в новые',
            callback_data=f'move-order created {order_id}',
        )])
    if isinstance(status, OrderStatus.DISPUTE):
        keyboard.append([InlineKeyboardButton(
            text='Перенести в обработанные',
            callback_data=f'move-order completed {order_id}',
        )])
    if isinstance(status, (OrderStatus.CREATED, OrderStatus.COMPLETED)):
        keyboard.append([InlineKeyboardButton(
            text='Удалить заявку',
            callback_data=f'delete-order {order_id}',
        )])
    if isinstance(status, OrderStatus.CREATED):
        keyboard.append([InlineKeyboardButton(
            text='Изменить данные',
            callback_data=f'edit-order {order_id}'
        )])
    
    keyboard.append(
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'admin orders'), in_menu_btn],
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def edit_order(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сумму заявки', callback_data=f'edit-amount-order {order_id}')],
        [InlineKeyboardButton(text='Карту', callback_data=f'edit-card-order {order_id}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'order-menu {order_id}')],
        [in_menu_btn],
    ])


def confirm_delete_order(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='❗ Да, удалить', callback_data=f'confirm-delete-order {order_id}'),
         InlineKeyboardButton(text='Отменить действие', callback_data=f'order-menu {order_id}')],
    ])


participants_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить участника', callback_data='add-participant-menu')],
    [InlineKeyboardButton(text='Активные участники', callback_data='active-participant')],
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

    if isinstance(role, (UserRole.OPERATOR, UserRole.PROVIDER)):
        keyboard.append([InlineKeyboardButton(
            text='Изменить комиссию',
            callback_data=f'edit-participant-commission {user_pk}',
        )])
        keyboard.append([InlineKeyboardButton(
            text='Изменить баланс',
            callback_data=f'edit-participant-balance {user_pk}',
        )])
    if isinstance(role, UserRole.PROVIDER):
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
