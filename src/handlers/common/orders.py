import hashlib
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import OrderStatus, order_status_to_text
from src.database.enums.user import UserRole
from src.keyboards import orders as kb
from src.filters.role import RoleFilter
from src.filters.common import amount_filter, card_filter
from src.utils.edit_message import EditMessage
from src.utils.other import generate_rand_string
from src.states.admin import EditOrderState


router = Router(name=__name__)
orders_filter = RoleFilter(UserRole.OWNER, UserRole.ADMIN, UserRole.OPERATOR)
router.message.filter(orders_filter)
router.callback_query.filter(orders_filter)

logger = logging.getLogger(__name__)


async def send_placeholder(query: InlineQuery) -> None:
    await query.answer(
        results=[InlineQueryResultArticle(
            id=hashlib.md5(generate_rand_string(8).encode()).hexdigest(),
            input_message_content=InputTextMessageContent(
                message_text=f'Ничего не было найдено',
            ),
            title='Заявок нет',
            description='Ничего не было найдено',
            reply_markup=kb.in_menu,
        )],
        cache_time=5,
        is_personal=True,
    )


@router.callback_query(F.data == 'orders')
async def admin_orders_menu(call: CallbackQuery) -> None:
    await EditMessage(call)(
        text='<b>Выберите тип заявки</b>',
        reply_markup=kb.orders_menu,
    )


@router.inline_query(F.query.startswith('order'))
async def order_inline(query: InlineQuery) -> None:
    user = await db.user.get(user_id=query.from_user.id)

    if query.query == 'order':
        status = ''
        search_query = []
    else:
        try:
            _, status, *search_query = query.query.split()
        except ValueError:
            logger.warning(f'Invalid query: "{query.query}"')
            return

    offset = query.offset or 0
    orders = await db.order.search(
        status=OrderStatus._value2member_map_.get(status),
        search_query=' '.join(search_query),
        offset=offset,
        **({'operator': user} if user.role is UserRole.OPERATOR else {}),
    )

    if len(orders) == 0:
        return await send_placeholder(query)

    await query.answer(
        results=[InlineQueryResultArticle(
            id=hashlib.md5(generate_rand_string(8).encode()).hexdigest(),
            input_message_content=InputTextMessageContent(
                message_text=order.get_message(user.role),
            ),
            title=order.title,
            description=order.description,
            reply_markup=kb.order_el(order.id, order.status, user.role),
        ) for order in orders],
        cache_time=5,
        is_personal=True,
        next_offset=offset + 1 if len(orders) >= 49 else None,
    )


@router.callback_query(F.data.startswith('order-menu'))
async def order_menu(call: CallbackQuery, state: FSMContext) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    await state.clear()
    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))

    await EditMessage(call)(
        text=order.get_message(user.role),
        reply_markup=kb.order_el(order.id, order.status, user.role),
    )


@router.callback_query(F.data.startswith('move-order'))
async def move_order(call: CallbackQuery) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    _, new_status, order_id = call.data.split()
    order = await db.order.update(
        order_id=int(order_id),
        status=OrderStatus(new_status),
    )

    await call.messsage.edit_text(
        text=f'{order.get_message(user.role)}\n\nЗаявка перенесена в <i>{order_status_to_text[order.status]}</i>',
        reply_markup=kb.order_el(order.id, order.status, user.role),
    )


@router.callback_query(F.data.startswith('delete-order'))
async def delete_order(call: CallbackQuery) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))

    await EditMessage(call)(
        text=f'{order.get_message(user.role)}\n\n'
            '<b>❗❗Подтвердите удаление заявки\nВсе, связанные с ней данные будут удалены!</b>',
        reply_markup=kb.confirm_delete_order(order.id),
    )


@router.callback_query(F.data.startswith('confirm-delete-order'))
async def confirm_delete_order(call: CallbackQuery) -> None:
    _, order_id = call.data.split()
    await db.order.delete(order_id=int(order_id))

    await EditMessage(call)(
        text=f'Заявка <b>#{order_id}</b> удалена',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('edit-order'))
async def edit_order(call: CallbackQuery) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))

    await EditMessage(call)(
        text=f'{order.get_message(user.role)}\n\n<b>Изменение заявки</b>\n<i>Выберите, что хотите изменить</i>',
        reply_markup=kb.edit_order(order.id),
    )


@router.callback_query(F.data.startswith('edit-amount-order'))
async def edit_order_amount(call: CallbackQuery, state: FSMContext) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))
    await state.set_state(EditOrderState.amount)
    await state.update_data(order_id=order.id)

    await EditMessage(call)(
        text=f'{order.get_message(user.role)}\n\n<b>Изменение суммы заявки</b>\n<i>Укажите новую сумму</i>',
        reply_markup=kb.cancel,
    )


@router.message(EditOrderState.amount, amount_filter)
async def set_order_amount(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await db.order.update(
        order_id=data['order_id'],
        amount=float(message.text),
    )

    await message.answer(
        text=f'Сумма заявки <b>{data["order_id"]}</b> изменена на <code>{message.text}</code>',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('edit-card-order'))
async def edit_order_card(call: CallbackQuery, state: FSMContext) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))
    await state.set_state(EditOrderState.card)
    await state.update_data(order_id=order.id)

    await EditMessage(call)(
        text=f'{order.get_message(user.role)}\n\n<b>Изменение карты заявки</b>\n<i>Укажите новую карту</i>',
        reply_markup=kb.cancel,
    )


@router.message(EditOrderState.card, card_filter)
async def set_order_card(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await db.order.update(
        order_id=data['order_id'],
        card=message.text,
    )

    await message.answer(
        text=f'Карта заявки <b>{data["order_id"]}</b> изменена на <code>{message.text}</code>',
        reply_markup=kb.in_menu,
    )
