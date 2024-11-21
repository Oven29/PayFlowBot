import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserRole, user_role_to_text, user_role_to_access_type
from src.database.enums.user import UserProviderStatus
from src.keyboards import admin as kb
from src.filters.common import number_filter
from src.filters.role import AdminFilter
from src.states.admin import AddParticipantState, EditParticipantState
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
    _, user_pk = call.data.split()
    user = await db.user.get(user_pk=int(user_pk))
    await state.update_data(user_pk=user.id)
    await state.set_state(EditParticipantState.commission)

    await EditMessage(call)(
        text=f'{user.message}\n\n<b>Изменение комиссии</b>\n<i>Укажите новую комиссию</i>',
        reply_markup=kb.cancel,
    )


@router.message(number_filter, EditParticipantState.commission)
async def set_participant_commission(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    user = await db.user.update(
        user_pk=data['user_pk'],
        commission=int(message.text),
    )

    await message.answer(
        text=f'Комиссия пользователя <b>{user.title}</b> изменена на <code>{message.text}</code>',
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


@router.message(number_filter, EditParticipantState.balance)
async def set_participant_balance(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    user = await db.user.update(
        user_pk=data['user_pk'],
        balance=int(message.text),
    )

    await message.answer(
        text=f'Баланс пользователя <b>{user.title}</b> изменен на <code>{message.text}</code>',
        reply_markup=kb.in_menu,
    )


@router.callback_query(F.data.startswith('disable-provider'))
async def disable_provider(call: CallbackQuery) -> None:
    _, user_pk = call.data.split()
    user = await db.user.get(user_pk=int(user_pk))

    if user.provider_status is UserProviderStatus.INACTIVE:
        return await call.answer(
            text='Пользователь уже неактивен',
            show_alert=True,
        )

    await db.user.update(
        user=user,
        status=UserProviderStatus.INACTIVE,
    )
    await call.answer(
        text='Пользователь успешно выключен',
        show_alert=True,
    )
