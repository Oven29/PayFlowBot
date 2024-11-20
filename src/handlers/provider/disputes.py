from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src import config
from src.database import db
from src.database.enums import OrderStatus, UserRole, UserProviderStatus, order_bank_to_text
from src.keyboards import provider as kb
from src.utils.edit_message import EditMessage
from src.filters.role import ProviderFilter


router = Router(name=__name__)
router.message.filter(ProviderFilter())
router.callback_query.filter(ProviderFilter())


@router.callback_query(F.data == 'provider-disputes')
async def menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    provider_orders = await db.order.get_user_orders(provider_id=call.from_user.id)
    dispute_orders = [order for order in provider_orders if order.status is OrderStatus.DISPUTE]

    await EditMessage(call)(
        text=f'<b>Диспуты:</b>\n\n'
            f'Замороженный баланс: {sum(order.amount for order in dispute_orders)}\n'
            f'Количество дисутов: {len(dispute_orders)} ({round(len(dispute_orders) / (len(provider_orders) or 1), 2)}%)',
        reply_markup=kb.dispute_list(dispute_orders),
    )


@router.callback_query(F.data.startswith('dispute-order'))
async def dispute_order(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))

    await EditMessage(call)(
        text=order.get_message(UserRole.PROVIDER),
        reply_markup=kb.dispute_order(order.id),
    )


@router.callback_query(F.data.startswith('cancel-dispute'))
async def move_order(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    if user.provider_status is UserProviderStatus.BUSY:
        state_data = await state.get_data()
        if 'order_id' in state_data:
            order = await db.order.get(order_id=state_data['order_id'])
        else:
            order = await db.order.get_current(provider_id=call.from_user.id)

        if not order is None:
            return await EditMessage(call)(
                text='<b>Есть незакрытая заявка!</b>\n\n'
                    f'Заявка #{order.id} принята\n'
                    f'Банк: <b>{order_bank_to_text[order.bank]}</b>\n'
                    f'Номер карты (телефона): <code>{order.card}</code>\n'
                    f'Сумма: <code>{order.amount}</code>',
                reply_markup=kb.finish_order(order.id),
            )

    _, order_id = call.data.split()
    order = await db.order.update(
        order_id=int(order_id),
        status=OrderStatus.PROCESSING,
        dispute_reason=None,
    )
    await bot.send_message(
        chat_id=config.ORDER_CHAT_ID,
        text=f'Диспут по заявке <b>{order.title}</b> отменен',
    )

    await EditMessage(call)(
        text=f'Заявка возвращена в активные\n\n{order.get_message(user.role)}',
        reply_markup=kb.finish_order(order.id),
    )
