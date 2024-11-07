import hashlib
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserRole, user_role_to_text, user_role_to_access_type
from src.keyboards import admin as kb
from src.filters.common import amount_filter, number_filter
from src.filters.role import AdminFilter
from src.states.admin import AddParticipantState, EditOrderState
from src.utils.edit_message import EditMessage
from src.utils.other import generate_rand_string


router = Router(name=__name__)
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


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
    else:
        return await message.answer(
            text='Некорректный ввод',
            reply_markup=kb.cancel,
        )

    data = await state.get_data()
    await state.clear()
    user_role = UserRole._member_map_[data['role']]
    token = await db.token.create(
        access_type=user_role_to_access_type[user_role],
        user_id=user_id,
        username=username,
    )

    await message.answer(
        text=f'<code>{token.link}</code>\n\n<i>Отправьте пользователю эту ссылку, '
            f'чтобы назначить его <b>{user_role_to_text[user_role]}</b></i>\n\n'
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
    try:
        _, role, *search_query = query.query.split()
    except ValueError:
        return

    offset = query.offset or 0
    if not role in UserRole._value2member_map_:
        search_query = (role, *search_query)
    users = await db.order.search(
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
        cache_time=30,
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
    await state.set_state(EditOrderState.commission)

    await EditMessage(call)(
        text=f'{user.message}\n\n<b>Изменение комиссии</b>\n<i>Укажите новую комиссию</i>',
        reply_markup=kb.cancel,
    )


@router.message(amount_filter, EditOrderState.commission)
async def set_participant_commission(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    user = await db.user.update(
        user_pk=data['user_pk'],
        commission=float(message.text),
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
    await state.set_state(EditOrderState.balance)

    await EditMessage(call)(
        text=f'{user.message}\n\n<b>Изменение баланса</b>\n<i>Укажите новый баланс</i>',
        reply_markup=kb.cancel,
    )


@router.message(number_filter, EditOrderState.balance)
async def set_participant_balance(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    user = await db.user.update(
        user_pk=data['user_pk'],
        balance=message.text,
    )

    await message.answer(
        text=f'Баланс пользователя <b>{user.title}</b> изменен на <code>{message.text}</code>',
        reply_markup=kb.in_menu,
    )
