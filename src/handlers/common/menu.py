from aiogram import Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import OrderStatus
from src.keyboards import common as kb
from src.utils.edit_message import EditMessage
from src.filters.role import AdminFilter, ManagerFilter, OperatorFilter, ProviderFilter


router = Router(name=__name__)


@router.message(or_f(CommandStart(), Command('admin')), AdminFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), AdminFilter())
async def admin_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text=f'<b>Добро пожаловать, {event.from_user.first_name}!</b>',
        reply_markup=kb.admin_menu,
    )


@router.message(or_f(CommandStart(), Command('operator')), OperatorFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), OperatorFilter())
async def operator_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    orders = await db.order.get_user_orders(opearator_id=event.from_user.id)
    active_orders = [order for order in orders if order.status in (OrderStatus.CREATED, OrderStatus.PROCESSING)]
    cancelled_orders = [order for order in orders if order.status is OrderStatus.CANCELLED]
    user = await db.user.get(user_id=event.from_user.id)

    await EditMessage(event)(
        text=f'<b>Меню оператора</b>\n\n'
            f'<b>Кол-во заявок в работе:</b> {len(active_orders)}\n'
            f'<b>Кол-во отменённых заявок:</b> {len(cancelled_orders)}\n'
            f'<b>Баланс:</b> {user.balance}\n'
            f'<b>Комиссия:</b> {user.commission}',
        reply_markup=kb.operator_menu,
    )


@router.message(or_f(CommandStart(), Command('provider')), ProviderFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), ProviderFilter())
async def provider_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    orders = await db.order.get_user_orders(provider_id=event.from_user.id)
    active_orders = [order for order in orders if order.status in (OrderStatus.CREATED, OrderStatus.PROCESSING)]
    cancelled_orders = [order for order in orders if order.status is OrderStatus.CANCELLED]
    disput_orders = [order for order in orders if order.status is OrderStatus.DISPUTE]
    user = await db.user.get(user_id=event.from_user.id)

    await EditMessage(event)(
        text=f'<b>Меню провайдера</b>\n\n'
            f'<b>Кол-во заявок в работе:</b> {len(active_orders)}\n'
            f'<b>Кол-во отменённых заявок:</b> {len(cancelled_orders)}\n'
            f'<b>Баланс:</b> {user.balance}\n'
            f'<b>Комиссия:</b> {user.commission}\n'
            f'<b>Замороженный общий баланс всех диспутов:</b> {sum(order.amount for order in disput_orders)}',
        reply_markup=kb.operator_menu,
    )


@router.message(or_f(CommandStart(), Command('manager')), ManagerFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), ManagerFilter())
async def manager_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text='Меню менеджера',
        reply_markup=kb.manager_menu,
    )
