import hashlib
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserRole, OrderStatus, order_status_to_text
from src.keyboards import admin as kb
from src.filters.role import AdminFilter
from src.filters.common import amount_filter, card_filter
from src.misc.utils import generate_rand_string
from src.states.admin import EditOrderState


router = Router(name=__name__)
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.callback_query(F.data == 'admin orders')
async def admin_orders_menu(call: CallbackQuery) -> None:
    await call.message.edit_text(
        text='Выберите тип заявки',
        reply_markup=kb.orders_menu,
    )


@router.inline_query(F.query.startswith('order_'))
async def order_inline(query: InlineQuery) -> None:
    try:
        _, status, *search_query = query.query.split()
    except ValueError:
        return

    offset = query.offset or 0
    orders = await db.order.search(
        status=OrderStatus._value2member_map_.get(status, OrderStatus.CREATED),
        search_query=' '.join(search_query),
        offset=offset,
    )

    await query.answer(
        results=[InlineQueryResultArticle(
            id=hashlib.md5(generate_rand_string(8).encode()).hexdigest(),
            input_message_content=InputTextMessageContent(
                message_text=order.message,
            ),
            title=order.title,
            description=order.description,
            reply_markup=kb.order_el(order.id, order.status),
        ) for order in orders],
        cache_time=30,
        is_personal=True,
        next_offset=offset + 1 if len(orders) >= 49 else None,
    )


@router.callback_query(F.data.startswith('move-order'))
async def move_order(call: CallbackQuery) -> None:
    _, new_status, order_id = call.data.split()
    order = await db.order.update(
        order_id=int(order_id),
        status=OrderStatus._member_map_[new_status],
    )

    await call.messsage.edit_text(
        text=f'Заявка <b>{order.title}</b> перенесена в <i>{order_status_to_text[order.status]}</i>',
        reply_markup=kb.orders_menu,
    )


@router.callback_query(F.data.startswith('delete-order'))
async def delete_order(call: CallbackQuery) -> None:
    _, order_id = call.data.split()
    await db.order.delete(order_id=int(order_id))

    await call.message.edit_text(
        text=f'Заявка <b>№{order_id}</b> удалена',
        reply_markup=kb.orders_menu,
    )


@router.callback_query(F.data.startswith('edit-order'))
async def edit_order(call: CallbackQuery) -> None:
    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))

    await call.message.edit_text(
        text=f'Изменение заявки <b>{order.title}</b>\n\n<i>Выберите, что хотите изменить</i>',
        reply_markup=kb.edit_order(order.id),
    )


@router.callback_query(F.data.startswith('edit-amount-order'))
async def edit_order_amount(call: CallbackQuery, state: FSMContext) -> None:
    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))
    await state.set_state(EditOrderState.amount)
    await state.update_data(order_id=order.id)

    await call.message.edit_text(
        text=f'Изменение суммы заявки <b>{order.title}</b>\n\n<i>Укажите новую сумму</i>',
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
    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))
    await state.set_state(EditOrderState.card)
    await state.update_data(order_id=order.id)

    await call.message.edit_text(
        text=f'Изменение карты заявки <b>{order.title}</b>\n\n<i>Укажите новую карту</i>',
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
