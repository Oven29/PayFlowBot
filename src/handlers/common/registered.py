import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .menu import admin_menu, operator_menu, provider_menu, manager_menu

from src.database import db
from src.database.enums import access_type_to_user_role
from src.database.enums.user import UserProviderStatus, UserRole
from src.keyboards import common as kb


router = Router(name=__name__)

logger = logging.getLogger(__name__)


async def get_menu_by_role(message: Message, state: FSMContext, role: UserRole) -> None:
    if role in (UserRole.ADMIN, UserRole.OWNER):
        await admin_menu(message, state)

    elif role is UserRole.OPERATOR:
        await operator_menu(message, state)

    elif role is UserRole.PROVIDER:
        await provider_menu(message, state)

    elif role is UserRole.MANAGER:
        await manager_menu(message, state)


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    _, *args = message.text.split()
    await state.clear()

    user = await db.user.get(user_id=message.from_user.id)

    if not args and user is None:
        return await message.answer(
            text='Вы не имеете доступ к боту',
        )

    if not args and not user is None:
        return await get_menu_by_role(message, state, user.role)

    code = args[0]
    token = await db.token.get_by_code(code)
    logger.info(f'Checking token=({token}) by {code=}')

    if token is None or not token.check_available(message.from_user.id, message.from_user.username):
        return await message.answer(
            text='Ссылка недействительна',
        )

    user, created = await db.user.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        role=access_type_to_user_role[token.access_type],
    )

    await db.token.close(token=token, user=user)

    if not created:
        role = access_type_to_user_role[token.access_type]
        user = await db.user.update(
            user=user,
            role=role,
            **({'provider_status': UserProviderStatus.INACTIVE} if role is UserRole.PROVIDER else {}),
        )

    return await get_menu_by_role(message, state, user.role)


@router.message(Command('freeze'))
async def freeze(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db.user.update(
        user_id=message.from_user.id,
        role=UserRole.IS_FREEZE,
        provider_status=UserProviderStatus.INACTIVE,
    )

    await message.answer(
        text='Аккаунт заморожен',
    )

@router.message(Command('remove'))
async def remove(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(
        text='Подтвредите удаление аккаунта\n<b>❗ Внимание, после удаления аккаунта вы потеряете все связанные данные</b>',
        reply_markup=kb.confirm_remove_account,
    )


@router.callback_query(F.data.startswith('confirm-remove-account'))
async def confirm_remove_account(call: CallbackQuery) -> None:
    await db.user.delete(user_id=call.from_user.id)
    await call.message.answer(text='Пока')
