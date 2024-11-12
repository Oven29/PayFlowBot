from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserProviderStatus, provider_status_to_text
from src.filters.role import ProviderFilter
from src.keyboards import provider as kb
from src.states.provider import RejectOrderState, CancelOrderState, DisputeOrderState, ConfirmOrderState
from src.utils.edit_message import EditMessage


router = Router(name=__name__)
router.message.filter(ProviderFilter())
router.callback_query.filter(ProviderFilter())


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
async def get_check(message: Message, state: FSMContext) -> None:
    pass
