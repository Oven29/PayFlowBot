from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserRole, access_type_to_user_role
from src.keyboards import common as kb
from src.filters.role import RoleFilter


router = Router(name=__name__)


@router.message(CommandStart(), RoleFilter(UserRole.OWNER, UserRole.ADMIN))
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), RoleFilter(UserRole.OWNER, UserRole.ADMIN))
async def admin_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    message = event if isinstance(event, Message) else event.message
    await message.answer(
        text='Меню администратора',
        reply_markup=kb.admin_menu,
    )


@router.message(CommandStart(), RoleFilter(UserRole.OPERATOR))
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), RoleFilter(UserRole.OPERATOR))
async def operator_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    message = event if isinstance(event, Message) else event.message
    await message.answer(
        text='Меню оператора',
        reply_markup=kb.operator_menu,
    )


@router.message(CommandStart(), RoleFilter(UserRole.PROVIDER))
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), RoleFilter(UserRole.PROVIDER))
async def provider_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    message = event if isinstance(event, Message) else event.message
    await message.answer(
        text='Меню провайдера',
        reply_markup=kb.provider_menu,
    )


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

    await db.user.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        role=access_type_to_user_role[token.access_type],
    )

    await message.answer(
        text='Добро пожаловать в бота!\nНажмите /start для открытия меню',
    )
