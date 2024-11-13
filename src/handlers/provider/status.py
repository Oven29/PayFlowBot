from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserProviderStatus, provider_status_to_text
from src.database.enums.user import UserRole
from src.keyboards import provider as kb
from src.utils.edit_message import EditMessage
from src.utils.distribute_order import go_on_shift
from src.filters.role import ProviderFilter


router = Router(name=__name__)
router.message.filter(ProviderFilter())
router.callback_query.filter(ProviderFilter())


@router.callback_query(F.data == 'start-work')
async def start_work(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    user = await db.user.get(user_id=call.from_user.id)
    if not user.provider_status is UserProviderStatus.INACTIVE and not user.role is UserRole.OWNER:
        return await call.answer(
            text='Завершите текущую сессию, чтобы начать новую',
            show_alert=True,
        )

    await EditMessage(call)(
        text='<b>Выберите направление</b>',
        reply_markup=kb.select_status,
    )


@router.callback_query(F.data.startswith('select-status'))
async def select_status(call: CallbackQuery) -> None:
    _, status = call.data.split()
    status = UserProviderStatus(status)

    await EditMessage(call)(
        text=f'<b>{status.name}</b>\nСтатус 🟥 off',
        reply_markup=kb.turn_on_status(status),
    )


@router.callback_query(F.data.startswith('turn-on-status'))
async def turn_on_status(call: CallbackQuery, state: FSMContext) -> None:
    _, status = call.data.split()
    await state.update_data(status=status)
    status = UserProviderStatus(status)

    user = await db.user.update(
        user_id=call.from_user.id,
        provider_status=status,
    )

    await EditMessage(call)(
        text=f'<b>{provider_status_to_text[status]}</b>\nСтатус 🟩 on\n\nОжидайте, бот будет отправлять Вам заявки\n\n'
            '<i>Для завершения сессии воспользуйтесь кнопкой ниже или командой /turn_off</i>',
        reply_markup=kb.turn_off_status,
    )
    await go_on_shift(user)


@router.callback_query(F.data == 'turn-off-status')
@router.message(Command('turn_off'))
async def turn_off_status(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await db.user.update(
        user_id=event.from_user.id,
        provider_status=UserProviderStatus.INACTIVE,
    )

    await EditMessage(event)(
        text='Статус 🟥 off',
        reply_markup=kb.in_menu,
    )
