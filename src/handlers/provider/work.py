import logging
from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src import config
from src.database import db
from src.database.enums import UserProviderStatus, CheckStatus, provider_status_to_text
from src.database.enums.order import OrderStatus
from src.filters.role import ProviderFilter
from src.keyboards import provider as kb
from src.states.provider import RejectOrderState, CancelOrderState, DisputeOrderState, ConfirmOrderState
from src.utils.check.tink import TinkCheck, BaseCheckException
from src.utils.edit_message import EditMessage
from src.utils.notifier import admin_notify


router = Router(name=__name__)
router.message.filter(ProviderFilter())
router.callback_query.filter(ProviderFilter())

logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith('reject-order'))
async def reject_order(event: CallbackQuery, state: FSMContext) -> None:
    _, order_id = event.data.split()
    order_id = int(order_id)
    await state.update_data(order_id=order_id)
    await state.set_state(RejectOrderState.reason)

    await EditMessage(event)(
        text='Введите причину отказа от заявки',
        reply_markup=kb.accept_order(order_id, reject_button=False),
    )


@router.message(F.text, RejectOrderState.reason)
async def reject_order_reason(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    await state.clear()
    status = UserProviderStatus(state_data['status']) if 'status' in state_data else UserProviderStatus.INACTIVE
    await state.update_data()

    user = await db.user.update(
        user_id=message.from_user.id,
        provider_status=status,
    )
    order = await db.order.reject(
        provider=user,
        reason=message.text,
        oreder_id=state_data['order_id'],
    )

    await EditMessage(message)(
        text=f'Заявка <b>{order.title}</b> отклонена\n'
            f'Сессия продолжается, банк: <b>{provider_status_to_text[status]}</b>',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('accept-order'))
async def accept_order(call: CallbackQuery, state: FSMContext) -> None:
    _, order_id = call.data.split()
    order = await db.order.get(order_id=int(order_id))

    await EditMessage(call)(
        text=f'Заявка №{order.id} принята\n'
            f'Банк: <b>{order.bank}</b>\n'
            f'Номер карты (телефона): <code>{order.card}</code>\n'
            f'Сумма: <code>{order.amount}</code>',
        reply_markup=kb.finish_order(order.id),
    )


@router.callback_query(F.data.startswith('finish-order'))
async def finish_order(call: CallbackQuery, state: FSMContext) -> None:
    _, order_id = call.data.split()
    await state.update_data(order_id=int(order_id))
    await state.set_state(ConfirmOrderState.check)

    await EditMessage(call)(
        text=f'{call.message.text}\n\n<b>Пришлите ссылку на чек</b>',
    )


@router.message(F.text, ConfirmOrderState.check)
async def get_check(message: Message, state: FSMContext, bot: Bot) -> None:
    state_data = await state.get_data()
    order = await db.order.get(
        order_id=state_data['order_id'],
    )
    check = TinkCheck(message.text, order.card)

    try:
        await check.valid()
    except BaseCheckException as e:
        await db.check.create(
            amount=check.amount,
            status=CheckStatus.ERROR,
            url=check.url,
            order=order,
        )
        return await message.answer(
            text='<b>Чек не прошел проверку, пожалуйста проверьте реквезиты и '
                f'скиньте чек ещё раз</b>\n\n<i>{e.message}</i>',
        )

    current_amount = state_data.get('current_amount', 0) + check.amount

    if current_amount < order.amount:
        await state.update_data(current_amount=current_amount)
        await db.check.create(
            amount=check.amount,
            status=CheckStatus.UNDERPAYMENT,
            url=check.url,
            order=order,
        )
        return await message.answer(
            text=f'<b>Сумма чека меньше суммы заявки</b>\n\n'
                f'<b>Сумма чека:</b> {check.amount}\n'
                f'<b>Сумма заявки:</b> {order.amount}\n'
                f'Доплатите {order.amount - check.amount} и пришлите чек',
        )

    note = ''
    check_status = CheckStatus.OK
    if current_amount > order.amount:
        note = f'\n\n! Сумма переплаты <b>{current_amount - order.amount}</b>'
        check_status = CheckStatus.OVERPAYMENT
        try:
            await bot.send_message(
                chat_id=config.OVERPAYEMNT_CHAT_ID,
                text=f'Переплата <i>{current_amount - order.amount}</i> по заявке {order.title}\n'
                    f'Оператор: {order.operator.title}\nПровайдер: {order.provider.title}',
            )
        except Exception as e:
            logger.warning(f'Error when sending overpayment notifier - {e}')

    await state.clear()
    await db.check.create(
        amount=check.amount,
        status=check_status,
        url=check.url,
        order=order,
    )
    await db.order.update(
        order=order,
        status=OrderStatus.COMPLETED,
    )
    user = await db.user.update(
        user=order.provider,
        provider_staus=UserProviderStatus(state_data.get('status', UserProviderStatus.INACTIVE.value)),
        balance=order.provider.calculate_balance(check.amount),
    )
    provider_orders = await db.order.get_user_orders(provider_id=message.from_user.id)

    await message.answer(
        text=f'Заявка <b>{order.title}</b> закрыта{note}\n\n'
            f'🟩 Смена продолжается <b>{provider_status_to_text[user.provider_status]}</b>\n'
            f'Баланс: {user.balance}\n'
            f'Диспут баланс: {sum(order.amount for order in provider_orders in order.status is OrderStatus.DISPUTE)}',
    )
    await bot.send_message(
        chat_id=order.provider.user_id,
        text=f'Заявка <b>{order.title}</b> закрыта',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('create-dispute'))
async def create_dispute(call: CallbackQuery, state: FSMContext) -> None:
    _, order_id = call.data.split()
    await state.update_data(order_id=int(order_id))
    await state.set_state(DisputeOrderState.reason)

    await EditMessage(call)(
        text='Введите причину открытия диспута\n<i>Например</i>\n<blockquote>Банкомат не дал чек</blockquote>',
    )


@router.message(F.text, DisputeOrderState.reason)
async def create_dispute_reason(message: Message, state: FSMContext, bot: Bot) -> None:
    state_data = await state.get_data()
    await state.clear()

    order = await db.order.update(
        order_id=state_data['order_id'],
        status=OrderStatus.DISPUTE,
        dispute_reason=message.text,
    )
    user = await db.user.update(
        user=order.provider,
        provider_staus=UserProviderStatus(state_data.get('status', UserProviderStatus.INACTIVE.value)),
    )
    provider_orders = await db.order.get_user_orders(provider_id=message.from_user.id)

    await message.answer(
        text=f'Создан диспут по заявке <b>{order.title}</b>\n\n'
            f'🟩 Смена продолжается <b>{provider_status_to_text[user.provider_status]}</b>\n'
            f'Баланс: {user.balance}\n'
            f'Диспут баланс: {sum(order.amount for order in provider_orders in order.status is OrderStatus.DISPUTE)}',
        )
    await bot.send_message(
        chat_id=order.operator.user_id,
        text=f'Создан диспут по заявке <b>{order.title}</b>',
        reply_markup=kb.in_menu,
    )
    await admin_notify(
        text=f'Создан диспут по заявке <b>{order.title}</b>',
        bot=bot,
    )
