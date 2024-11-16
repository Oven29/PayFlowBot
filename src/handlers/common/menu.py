from aiogram import Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import OrderStatus, UserProviderStatus, provider_status_to_text
from src.keyboards import common as kb
from src.utils.edit_message import EditMessage
from src.filters.role import AdminFilter, ManagerFilter, OperatorFilter, ProviderFilter


router = Router(name=__name__)


@router.message(Command('admin'), AdminFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu', 'admin-menu'}), AdminFilter())
async def admin_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text=f'<b>Добро пожаловать в меню администратора, {event.from_user.first_name}!</b>',
        reply_markup=kb.admin_menu,
    )


@router.message(Command('operator'), OperatorFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu', 'operator-menu'}), OperatorFilter())
async def operator_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    orders = await db.order.get_user_orders(opearator_id=event.from_user.id)
    completed_orders = [order for order in orders if order.status is OrderStatus.COMPLETED]
    active_orders = [order for order in orders if order.status in (OrderStatus.CREATED, OrderStatus.PROCESSING)]
    cancelled_orders = [order for order in orders if order.status is OrderStatus.CANCELLED]
    user = await db.user.get(user_id=event.from_user.id)

    await EditMessage(event)(
        text=f'<b>Меню оператора</b>\n\n'
            f'<b>Кол-во заявок в работе:</b> {len(active_orders)}\n'
            f'<b>Кол-во обработанных заявок:</b> {len(completed_orders)}\n'
            f'<b>Кол-во отменённых заявок:</b> {len(cancelled_orders)}\n'
            f'<b>Баланс:</b> {user.balance}\n'
            f'<b>Комиссия:</b> {user.commission}',
        reply_markup=kb.operator_menu,
    )


@router.message(Command('provider'), ProviderFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu', 'provider-menu'}), ProviderFilter())
async def provider_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user = await db.user.get(user_id=event.from_user.id)

    if not user.provider_status in (UserProviderStatus.INACTIVE, UserProviderStatus.NO_PROVIDER):
        return await EditMessage(event)(
            text=f'<b>{provider_status_to_text[user.provider_status]}</b>\n'
                'Статус 🟩 on\n\nОжидайте, бот будет отправлять Вам заявки\n\n'
                '<i>Для завершения сессии воспользойтесь командой /turn_off</i>',
        )

    orders = await db.order.get_user_orders(provider_id=event.from_user.id)
    completed_orders = [order for order in orders if order.status is OrderStatus.COMPLETED]
    cancelled_orders = [order for order in orders if order.status is OrderStatus.CANCELLED]
    disput_orders = [order for order in orders if order.status is OrderStatus.DISPUTE]

    await EditMessage(event)(
        text=f'<b>Меню провайдера</b>\n\n'
            f'<b>Кол-во диспутов:</b> {len(disput_orders)}\n'
            f'<b>Кол-во обработанных заявок:</b> {len(completed_orders)}\n'
            f'<b>Кол-во отменённых заявок:</b> {len(cancelled_orders)}\n'
            f'<b>Баланс:</b> {user.balance}\n'
            f'<b>Комиссия:</b> {user.commission}\n'
            f'<b>Замороженный общий баланс всех диспутов:</b> {sum(order.amount for order in disput_orders)}',
        reply_markup=kb.provider_menu,
    )


@router.message(Command('manager'), ManagerFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu', 'manager-menu'}), ManagerFilter())
async def manager_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text='Меню менеджера',
        reply_markup=kb.manager_menu,
    )


@router.callback_query(F.data.startswith('update-order-info'))
async def update_order_info(call: CallbackQuery) -> None:
    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))

    try:
        await call.message.edit_text(
            text=order.description,
            reply_markup=kb.update_order_info(order.id),
        )
    except:
        pass
