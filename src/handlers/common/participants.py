import hashlib
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserRole, user_role_to_text, user_role_to_access_type
from src.keyboards import participants as kb
from src.filters.role import RoleFilter
from src.states.common import AddParticipantState
from src.utils.edit_message import EditMessage
from src.utils.other import generate_rand_string


router = Router(name=__name__)
router.message.filter(RoleFilter(UserRole.ADMIN, UserRole.OWNER, UserRole.MANAGER))
router.callback_query.filter(RoleFilter(UserRole.ADMIN, UserRole.OWNER, UserRole.MANAGER))

logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'participants')
async def admin_participants(call: CallbackQuery) -> None:
    await EditMessage(call)(
        text='Участники',
        reply_markup=kb.participants_menu,
    )


@router.callback_query(F.data == 'add-participant-menu')
async def add_participant_menu(call: CallbackQuery) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    await EditMessage(call)(
        text='Пожалуйста выберите кого хотите добавить',
        reply_markup=kb.add_participant(user.role),
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
    elif not message.text in ('-', '—'):
        username = message.text

    data = await state.get_data()
    await state.clear()
    user_role = UserRole(data['role'])

    user = await db.user.get(user_id=message.from_user.id)
    token = await db.token.create(
        access_type=user_role_to_access_type[user_role],
        user_id=user_id,
        username=username.lower(),
        manager=user if user.role is UserRole.MANAGER else None,
    )

    await message.answer(
        text=f'<code>{token.link}</code>\n\n'
            f'<i>Отправьте пользователю ссылку или код, чтобы назначить его <b>{user_role_to_text[user_role]}</b></i>\n\n'
            '/start - Вернуться в меню',
    )


@router.callback_query(F.data == 'active-participants')
async def active_participants(call: CallbackQuery) -> None:
    user = await db.user.get(user_id=call.from_user.id)

    await EditMessage(call)(
        text='Выберите кто Вас интересует',
        reply_markup=kb.active_participants_menu(user.role),
    )

async def send_placeholder(query: InlineQuery) -> None:
    await query.answer(
        results=[InlineQueryResultArticle(
            id=hashlib.md5(generate_rand_string(8).encode()).hexdigest(),
            input_message_content=InputTextMessageContent(
                message_text=f'Ничего не было найдено',
            ),
            title='Пользователей нет',
            description='Ничего не было найдено',
            reply_markup=kb.in_menu,
        )],
        cache_time=5,
        is_personal=True,
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

    user = await db.user.get(user_id=query.from_user.id)
    if user.role is UserRole.MANAGER:
        pass

    offset = query.offset or 0
    users = await db.user.search(
        role=UserRole._value2member_map_.get(role),
        search_query=' '.join(search_query),
        offset=offset,
    )

    if user.role is UserRole.MANAGER:
        manager_users = await db.token.get_by_manager(manager=user)
        users = [user for user in users if user in manager_users]

    if len(users) == 0:
        return await send_placeholder(query)

    await query.answer(
        results=[InlineQueryResultArticle(
            id=hashlib.md5(generate_rand_string(8).encode()).hexdigest(),
            input_message_content=InputTextMessageContent(
                message_text=el.message,
            ),
            title=el.title,
            description=el.description,
            reply_markup=kb.user_el(el.id, el.role) if user.role in (UserRole.ADMIN, UserRole.OWNER) else kb.in_menu,
        ) for el in users],
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
        reply_markup=kb.user_el(user.id, user.role) if user.role in (UserRole.ADMIN, UserRole.OWNER) else kb.in_menu,
    )
