from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import access_type_to_user_role
from src.database.enums.user import UserRole
from src.keyboards import common as kb
from src.utils.edit_message import EditMessage
from src.filters.role import AdminFilter, ManagerFilter, OperatorFilter, ProviderFilter


router = Router(name=__name__)


@router.message(or_f(CommandStart(), Command('admin')), AdminFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), AdminFilter())
async def admin_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text='Меню администратора',
        reply_markup=kb.admin_menu,
    )


@router.message(or_f(CommandStart(), Command('operator')), OperatorFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), OperatorFilter())
async def operator_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text='Меню оператора',
        reply_markup=kb.operator_menu,
    )


@router.message(or_f(CommandStart(), Command('provider')), ProviderFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), ProviderFilter())
async def provider_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text='Меню провайдера',
        reply_markup=kb.provider_menu,
    )


@router.message(or_f(CommandStart(), Command('manager')), ManagerFilter())
@router.callback_query(F.data.in_({'cancel', 'main-menu'}), ManagerFilter())
async def manager_menu(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await EditMessage(event)(
        text='Меню менеджера',
        reply_markup=kb.manager_menu,
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
