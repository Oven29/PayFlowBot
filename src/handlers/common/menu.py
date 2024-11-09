from aiogram import Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

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
