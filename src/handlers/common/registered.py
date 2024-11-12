from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import access_type_to_user_role
from src.database.enums.user import UserProviderStatus, UserRole
from src.keyboards import common as kb


router = Router(name=__name__)


@router.message(CommandStart())
async def unregistered_start(message: Message, state: FSMContext, bot: Bot) -> None:
    _, *args = message.text.split()
    await state.clear()

    if not args:
        return await message.answer(
            text='Вы не имеете доступ к боту',
        )

    code = args[0]
    token = await db.token.get_by_code(code)

    if token is None or not token.check_available(message.from_user.id, message.from_user.username):
        return await message.answer(
            text='Ссылка недействительна',
        )

    user, created = await db.user.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        role=access_type_to_user_role[token.access_type],
    )

    if created:
        await db.token.close(token=token, user=user)

    if user.role is UserRole.IS_FREEZE:
        await db.user.update(
            user=user,
            role=access_type_to_user_role[token.access_type],
        )
        await db.token.close(token=token, user=user)

    await message.answer(
        text='Добро пожаловать в бота!\nНажмите /start для открытия меню',
    )


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
