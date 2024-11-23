import logging
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserProviderStatus, OrderBank, order_bank_to_text
from src.keyboards import admin as kb
from src.filters.common import AmountFilter
from src.filters.role import AdminFilter
from src.states.admin import EditParticipantState
from src.utils.edit_message import EditMessage


router = Router(name=__name__)
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith('delete-participant'))
async def delete_participant(call: CallbackQuery) -> None:
    _, user_pk = call.data.split()
    user = await db.user.get(user_pk=int(user_pk))

    await EditMessage(call)(
        text=f'{user.message}\n\n<b>❗❗Подтвердите удаление пользователя\nВсе, связанные с ним данные будут удалены!</b>',
        reply_markup=kb.confirm_delete_participant(user.id),
    )


@router.callback_query(F.data.startswith('confirm-delete-participant'))
async def confirm_delete_participant(call: CallbackQuery) -> None:
    _, user_pk = call.data.split()
    await db.user.delete(user_pk=int(user_pk))

    await EditMessage(call)(
        text=f'Пользователь удален',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('edit-participant-commission'))
async def edit_participant_commission(call: CallbackQuery, state: FSMContext) -> None:
    _, bank, user_pk = call.data.split()
    user = await db.user.get(user_pk=int(user_pk))
    await state.update_data(user_pk=user.id, bank=bank)
    await state.set_state(EditParticipantState.commission)

    await EditMessage(call)(
        text=f'{user.message}\n\n<b>Изменение комиссии {order_bank_to_text[OrderBank(bank)]}</b>'
            '\n<i>Укажите новую комиссию</i>',
        reply_markup=kb.cancel,
    )


@router.message(EditParticipantState.commission, AmountFilter(pass_value=True))
async def set_participant_commission(message: Message, state: FSMContext, value: float) -> None:
    state_data = await state.get_data()
    await state.clear()

    user = await db.user.get(user_pk=state_data['user_pk'])
    commissions = user.commissions or {}
    bank = OrderBank(state_data['bank'])
    commissions[bank] = value
    user = await db.user.update(
        user_pk=user.id,
        commission=commissions,
    )

    await message.answer(
        text=f'Комиссия {order_bank_to_text[bank]} пользователя <b>{user.title}</b> изменена на <code>{value}%</code>',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('edit-participant-balance'))
async def edit_participant_balance(call: CallbackQuery, state: FSMContext) -> None:
    _, user_pk = call.data.split()
    user = await db.user.get(user_pk=int(user_pk))
    await state.update_data(user_pk=user.id)
    await state.set_state(EditParticipantState.balance)

    await EditMessage(call)(
        text=f'{user.message}\n\n<b>Изменение баланса</b>\n<i>Укажите новый баланс</i>',
        reply_markup=kb.cancel,
    )


@router.message(EditParticipantState.balance, AmountFilter(pass_value=True))
async def set_participant_balance(message: Message, state: FSMContext, value: float) -> None:
    data = await state.get_data()
    await state.clear()
    user = await db.user.update(
        user_pk=data['user_pk'],
        balance=int(value),
    )

    await message.answer(
        text=f'Баланс пользователя <b>{user.title}</b> изменен на <code>{value}</code>',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('disable-provider'))
async def disable_provider(call: CallbackQuery, bot: Bot) -> None:
    _, user_pk = call.data.split()
    user = await db.user.get(user_pk=int(user_pk))

    if user.provider_status is UserProviderStatus.INACTIVE:
        return await call.answer(
            text='Пользователь уже неактивен',
            show_alert=True,
        )

    await db.user.update(
        user=user,
        provider_status=UserProviderStatus.INACTIVE,
    )
    await call.answer(
        text='Пользователь успешно выключен',
        show_alert=True,
    )
    await bot.send_message(
        chat_id=user.user_id,
        text='Статус 🟥 off',
        reply_markup=kb.in_menu,
    )
