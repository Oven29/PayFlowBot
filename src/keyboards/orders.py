from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu
from src.database.enums import OrderStatus, order_status_to_text, UserRole


orders_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔍 Поиск по всем заявкам', switch_inline_query_current_chat='order ')],
] + [
    [InlineKeyboardButton(text=text, switch_inline_query_current_chat=f'order {status.value} ')]
      for status, text in order_status_to_text.items()
] + [
    [InlineKeyboardButton(text='🔙 В меню', callback_data='main-menu')],
])


def order_el(order_id: int, status: OrderStatus, role: UserRole) -> InlineKeyboardMarkup:
    keyboard = []

    if status is OrderStatus.CANCELLED:
        keyboard.append([InlineKeyboardButton(
            text='Перенести в новые',
            callback_data=f'move-order created {order_id}',
        )])
    if status is OrderStatus.DISPUTE and role in (UserRole.OWNER, UserRole.ADMIN):
        keyboard.append([InlineKeyboardButton(
            text='Перенести в обработанные',
            callback_data=f'move-order completed {order_id}',
        )])
    if status is OrderStatus.COMPLETED and role in (UserRole.OWNER, UserRole.ADMIN) or \
        status in (OrderStatus.CREATED, OrderStatus.PROCESSING):
        keyboard.append([InlineKeyboardButton(
            text='Удалить заявку',
            callback_data=f'delete-order {order_id}',
        )])
    if status is OrderStatus.CREATED:
        keyboard.append([InlineKeyboardButton(
            text='Изменить данные',
            callback_data=f'edit-order {order_id}'
        )])

    keyboard.append(
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'orders'), in_menu_btn],
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
