from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .common import cancel_btn, cancel, in_menu_btn, in_menu
from src.database.enums import OrderStatus, order_status_to_text


orders_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔍 Поиск по всем заявкам', switch_inline_query_current_chat='order ')],
] + [
    [InlineKeyboardButton(text=text, switch_inline_query_current_chat=f'order {status.value} ')]
      for status, text in order_status_to_text.items()
] + [
    in_menu_btn,
])


def order_el(order_id: int, status: OrderStatus) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'admin participants')],
        in_menu_btn,
    ]

    if isinstance(status, OrderStatus.CANCELLED):
        keyboard.insert(0, [InlineKeyboardButton(
            text='Перенести в новые',
            callback_data=f'move-order created {order_id}',
        )])

    if isinstance(status, OrderStatus.DISPUTE):
        keyboard.insert(0, [InlineKeyboardButton(
            text='Перенести в обработанные',
            callback_data=f'move-order completed {order_id}',
        )])

    if isinstance(status, (OrderStatus.CREATED, OrderStatus.COMPLETED)):
        keyboard.insert(0, [InlineKeyboardButton(
            text='Удалить заявку',
            callback_data=f'delete-order {order_id}',
        )])

    if isinstance(status, OrderStatus.CREATED):
        keyboard.insert(0, [InlineKeyboardButton(
            text='Изменить данные',
            callback_data=f'edit-order {order_id}'
        )])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def edit_order(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сумму заявки', callback_data=f'edit-amount-order {order_id}')],
        [InlineKeyboardButton(text='Карту', callback_data=f'edit-card-order {order_id}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'order-menu {order_id}')],
        in_menu_btn,
    ])


def confirm_delete(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='❗ Да, удалить', callback_data=f'confirm-delete-order {order_id}')],
        [InlineKeyboardButton(text='Отменить действие', callback_data=f'order-menu {order_id}')],
    ])
