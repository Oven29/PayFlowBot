import hashlib
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserRole, user_role_to_text, user_role_to_access_type
from src.database.enums.user import UserProviderStatus
from src.keyboards import admin as kb
from src.filters.common import amount_filter, number_filter
from src.filters.role import AdminFilter
from src.states.admin import AddParticipantState, EditParticipantState
from src.utils.edit_message import EditMessage
from src.utils.other import generate_rand_string


router = Router(name=__name__)
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'admin participants')
async def admin_participants(call: CallbackQuery) -> None:
    await EditMessage(call)(
        text='Участники',
        reply_markup=kb.participants_menu,
    )


@router.callback_query(F.data == 'add-participant-menu')
async def add_participant_menu(call: CallbackQuery) -> None:
    await EditMessage(call)(
        text='Пожалуйста выберите кого хотите добавить',
        reply_markup=kb.add_participant,
    )


@router.callback_query(F.data.startswith('add-participant'))
async def add_participant(call: CallbackQuery, state: FSMContext) -> None:
    _, role = call.data.split() 
    await state.update_data(role=role)
    await state.set_state(AddParticipantState.input)

    await EditMessage(call)(
        text=f'<b>Добавление <i>{user_role_to_text[role]}</i></b>\n\nВведите username или telegram_id пользователя\n'
            f'Если хотите сделать ссылку общей (подходящей для любого) введите <blockquote><code>-</code></blockquote>',
        reply_markup=kb.cancel,
    )


@router.message(F.text, AddParticipantState.input)
async def add_participant_input(message: Message, state: FSMContext) -> None:
    user_id = None
    username = None

    if message.text.isdigit():
        user_id = int(message.text)
    elif message.text.startswith('@'):
        username = message.text[1:]
    elif message.text != '-':
        username = message.text

    data = await state.get_data()
    await state.clear()
    user_role = UserRole(data['role'])
    token = await db.token.create(
        access_type=user_role_to_access_type[user_role],
        user_id=user_id,
        username=username,
    )

    await message.answer(
        text=f'<code>{token.link}</code>\n\n'
            f'<i>Отправьте пользователю ссылку или код, чтобы назначить его <b>{user_role_to_text[user_role]}</b></i>\n\n'
            '/start - Вернуться в меню',
    )


@router.callback_query(F.data == 'active-participants')
async def active_participants(call: CallbackQuery) -> None:
    await EditMessage(call)(
        text='Выберите кто Вас интересует',
        reply_markup=kb.active_participants_menu,
    )


@router.inline_query(F.query.startswith('participant'))
async def participant_inline(query: InlineQuery, state: FSMContext) -> None:
    if query.query == 'participant':
        role = ''
        search_query = []
    else:
        try:
            _, role, *search_query = query.query.split()
        except ValueError:
            logger.warning(f'Invalid query: "{query.query}"')
            return

    offset = query.offset or 0
    users = await db.user.search(
        role=UserRole._value2member_map_.get(role),
        search_query=' '.join(search_query),
        offset=offset,
    )

    await query.answer(
        results=[InlineQueryResultArticle(
            id=hashlib.md5(generate_rand_string(8).encode()).hexdigest(),
            input_message_content=InputTextMessageContent(
                message_text=user.message,
            ),
            title=user.title,
            description=user.description,
            reply_markup=kb.user_el(user.id, user.role),
        ) for user in users],
        cache_time=5,
        is_personal=True,
        next_offset=offset + 1 if len(users) >= 49 else None,
    )


@router.callback_query(F.data.startswith('participant-menu'))
async def participant_menu(call: CallbackQuery) -> None:
    _, user_pk = call.data.split()
    user = await db.user.get(user_pk=int(user_pk))

    await EditMessage(call)(
        text=user.message,
        reply_markup=kb.user_el(user.id, user.role),
    )


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
