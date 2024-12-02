from datetime import datetime
import logging
from typing import Any, Dict
from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src import config
from src.database import db
from src.database.enums import UserProviderStatus, CheckStatus, CheckType, OrderStatus, provider_status_to_text
from src.filters.role import ProviderFilter
from src.keyboards import provider as kb
from src.states.provider import RejectOrderState, DisputeOrderState, ConfirmOrderState
from src.utils.check import TinkPdfCheck, TinkUrlCheck, BaseCheck, BaseCheckException
from src.utils.distribute_order import distribute_order, go_on_shift
from src.utils.edit_message import EditMessage
from src.utils.scheduler import remove_job_by_name_pattern


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
async def reject_order_reason(message: Message, state: FSMContext, bot: Bot) -> None:
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
        order_id=state_data['order_id'],
    )

    await bot.send_message(
        chat_id=config.REJECT_ORDER_CHAT_ID,
        text=f'Заявка <b>{order.title}</b> отклонена провайдером {user.title}',
    )

    rejects = await db.order.get_reject_orders(order)

    if len(rejects) == 3:
        text = f'Заказ <b>{order.title}</b> отменён из-за того, что провайдеры не приняли его много раз\n\n' \
            f'Причины отказов провайдеров:\n\n{"\n\n".join(el.reason for el in rejects)}'
        await bot.send_message(
            chat_id=config.ORDER_CHAT_ID,
            text=text,
        )
        await bot.send_message(
            chat_id=order.operator.user_id,
            text=text,
        )
        await db.order.update(
            order=order,
            status=OrderStatus.CANCELLED,
        )

    else:
        await distribute_order(order)

    await EditMessage(message)(
        text=f'Заявка <b>{order.title}</b> отклонена\n'
            f'Сессия продолжается, банк: <b>{provider_status_to_text[status]}</b>',
        reply_markup=kb.in_menu,
    )
    await go_on_shift(user)


@router.callback_query(F.data.startswith('accept-order'))
async def accept_order(call: CallbackQuery, state: FSMContext) -> None:
    _, order_id = call.data.split()
    user = await db.user.get(user_id=call.from_user.id)
    order = await db.order.update(
        order_id=int(order_id),
        provider=user,
        taking_date=datetime.now(),
    )
    await state.update_data(order_id=order.id)
    remove_job_by_name_pattern(f'*{call.from_user.id}')

    await EditMessage(call)(
        text=f'<b>Заявка принята</b>\n\n{order.get_message(user.role)}',
        reply_markup=kb.finish_order(order.id),
    )


@router.callback_query(F.data.startswith('finish-order'))
async def wait_check(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ConfirmOrderState.check)

    await EditMessage(call)(
        text=f'{call.message.html_text}\n\n<b>Пришлите ссылку на чек или отправьте его PDF файлом</b>',
    )


@router.message(ConfirmOrderState.check, F.text)
@router.message(ConfirmOrderState.check, F.document.mime_type == 'application/pdf')
async def get_check(message: Message, state: FSMContext, bot: Bot) -> None:
    state_data = await state.get_data()

    if 'order_id' in state_data:
        order = await db.order.get(
            order_id=state_data['order_id'],
        )
    else:
        order = await db.order.get_current(provider_id=message.from_user.id)
        await state.update_data(order_id=order.id)

    if message.text:
        check_type = CheckType.URL
        check = TinkUrlCheck(message.text, order)
    else:
        check_type = CheckType.PDF
        check = TinkPdfCheck(message.document.file_id, order)

    if await db.check.check_exists_by_url(check.url):
        return await message.answer(
            text=f'Чек <i>{check.url}</i> уже был принят',
        )

    try:
        await check.valid()

    except BaseCheckException as e:
        await db.check.create(
            date=check.date,
            amount=check.amount,
            status=CheckStatus.ERROR,
            url=check.url,
            order=order,
            type=check_type,
        )
        return await message.answer(
            text='<b>Чек не прошел проверку, пожалуйста проверьте реквезиты и '
                f'скиньте чек ещё раз</b>\n\n<i>{e.message}</i>',
        )

    if check_type is CheckType.PDF:
        db_check = await db.check.create(
            date=check.date,
            amount=check.amount,
            status=CheckStatus.WAIT,
            url=check.url,
            order=order,
            type=check_type,
        )
        await bot.send_document(
            chat_id=config.CHECK_CHAT_ID,
            document=message.document.file_id,
            caption=f'Чек на <i>{check.amount}₽</i> по заявке <b>{order.title}</b>\n'
                f'Провайдер: {order.provider.title}\nОператор: {order.operator.title}',
            reply_markup=kb.accept_check(db_check.id),
        )
        return await message.answer(
            text='Чек отправлен на проверку администрации, можете скинуть ещё чеки, сумма текущего меньше суммы заявки',
        )

    await finish_order(message, state, bot, state_data, check_type, check, order)


@router.callback_query(F.data.startswith('save-check'))
async def save_check(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    _, check_id = call.data.split()
    db_check = await db.check.get_by_id(check_id=check_id)

    check = BaseCheck(
        url=db_check.url,
        order=db_check.order,
        date=db_check.date,
        amount=db_check.amount,
    )
    await db.check.delete(check_id=db_check.id)

    await finish_order(call.message, state, bot, (await state.get_data()), CheckType.PDF, check, db_check.order)


async def finish_order(
    message: Message,
    state: FSMContext,
    bot: Bot,
    state_data: Dict[str, Any],
    check_type: CheckType,
    check: BaseCheck,
    order: db.order.Order,
) -> None:
    current_amount = state_data.get('current_amount', 0) + check.amount

    if current_amount < order.amount:
        await state.update_data(current_amount=current_amount)
        await db.check.create(
            date=check.date,
            amount=check.amount,
            status=CheckStatus.UNDERPAYMENT,
            url=check.url,
            order=order,
            type=check_type,
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
        date=check.date,
        amount=check.amount,
        status=check_status,
        url=check.url,
        order=order,
        type=check_type,
    )
    await db.order.update(
        order=order,
        status=OrderStatus.COMPLETED,
        close_date=datetime.now(),
    )
    logger.info(f'Updating provider balance {order.provider.user_id}: {order.provider.balance=}, '
        f'{order.provider.commissions}, {order.id=}')
    provider = await db.user.update(
        user=order.provider,
        provider_status=UserProviderStatus(state_data.get('status', UserProviderStatus.INACTIVE.value)),
        balance=order.provider.calculate_balance(order.amount, order.bank),
    )
    provider_orders = await db.order.get_user_orders(provider_id=message.from_user.id)
    logger.info(f'Updating operator balance {order.operator.user_id}: {order.operator.balance=}, '
        f'{order.operator.commissions}, {order.id=}')
    await db.user.update(
        user=order.operator,
        balance=order.operator.calculate_balance(order.amount, order.bank),
    )

    if provider.provider_status is UserProviderStatus.INACTIVE:
        await message.answer(
            text=f'Статус 🟥 off',
            reply_markup=kb.in_menu,
        )
    else:
        await message.answer(
            text=f'Заявка <b>{order.title}</b> закрыта{note}\n\n'
                f'🟩 Смена продолжается <b>{provider_status_to_text[provider.provider_status]}</b>\n'
                f'Баланс: {provider.balance}₽\n'
                f'Диспут баланс: {sum(order.amount for order in provider_orders if order.status is OrderStatus.DISPUTE)}',
        )
        await go_on_shift(provider)

    await bot.send_message(
        chat_id=order.operator.user_id,
        text=f'Заявка <b>{order.title}</b> закрыта',
        reply_markup=kb.in_menu,
    )
    await bot.send_message(
        chat_id=config.ORDER_CHAT_ID,
        text=f'Заявка <b>{order.title}</b> закрыта',
    )

    provider_invite_link = await db.token.get_by_user(user=provider)
    if (manager := provider_invite_link.manager):
        logger.info(f'Updating manager balance {manager.user_id}: {manager.balance=}, '
            f'{manager.commissions}, {order.id=}')
        await db.user.update(
            user=manager,
            balance=manager.calculate_balance(order.amount, order.bank),
        )

    operator_invite_link = await db.token.get_by_user(user=order.operator)
    if (manager := operator_invite_link.manager):
        logger.info(f'Updating manager balance {manager.user_id}: {manager.balance=}, '
            f'{manager.commissions}, {order.id=}')
        await db.user.update(
            user=manager,
            balance=manager.calculate_balance(order.amount, order.bank),
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
        provider_status=UserProviderStatus(state_data.get('status', UserProviderStatus.INACTIVE.value)),
    )
    provider_orders = await db.order.get_user_orders(provider_id=message.from_user.id)

    await message.answer(
        text=f'Создан диспут по заявке <b>{order.title}</b>\n\n'
            f'🟩 Смена продолжается <b>{provider_status_to_text[user.provider_status]}</b>\n'
            f'Баланс: {user.balance}₽\n'
            f'Диспут баланс: {sum(order.amount for order in provider_orders if order.status is OrderStatus.DISPUTE)}',
        )
    await bot.send_message(
        chat_id=order.operator.user_id,
        text=f'Создан диспут по заявке <b>{order.title}</b>',
        reply_markup=kb.in_menu,
    )
    await bot.send_message(
        chat_id=config.ORDER_CHAT_ID,
        text=f'Создан диспут по заявке <b>{order.title}</b>',
    )
