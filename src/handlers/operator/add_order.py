from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import OrderBank, order_bank_to_text
from src.keyboards import operator as kb
from src.filters.common import amount_filter, number_filter
from src.filters.role import AdminFilter
from src.states.operator import AddOrderState
from src.utils.distribute_order import distribute_order


router = Router(name=__name__)
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.callback_query(F.data == 'add-order')
async def add_order(call: CallbackQuery) -> None:
    await call.message.edit_text(
        text=f'Выберите банк',
        reply_markup=kb.select_bank,
    )


@router.callback_query(F.data.startswith('select-bank'))
async def select_bank(call: CallbackQuery, state: FSMContext) -> None:
    _, bank = call.data.split()
    await state.update_data(bank=bank)
    await state.set_state(AddOrderState.uid)

    await call.message.edit_text(
        text='Введите номер заявки',
        reply_markup=kb.cancel,
    )


@router.message(F.text, AddOrderState.uid)
async def add_order_uid(message: Message, state: FSMContext) -> None:
    await state.update_data(uid=message.text)
    await state.set_state(AddOrderState.card)

    await message.answer(
        text='Введите карту (номер телефона)',
        reply_markup=kb.cancel,
    )


@router.message(AddOrderState.card, number_filter)
async def add_order_card(message: Message, state: FSMContext) -> None:
    await state.update_data(card=message.text)
    await state.set_state(AddOrderState.amount)

    await message.answer(
        text='Введите сумму',
        reply_markup=kb.cancel,
    )


@router.message(AddOrderState.card)
async def wrong_card(message: Message) -> None:
    await message.answer(
        text='Некорректный ввод\nТребуется ввести номер карты или телефона - числовое значение',
        reply_markup=kb.cancel,
    )


@router.message(AddOrderState.amount, amount_filter)
async def add_order_amount(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(amount=float(message.text))

    await message.answer(
        text='Подтвердите создание заявки:\n\n'
            f'Банк: {order_bank_to_text[OrderBank(data["bank"])]}\n'
            f'Карта: {data["card"]}\n'
            f'Сумма: {message.text}',
        reply_markup=kb.confirm_adding_order,
    )


@router.message(AddOrderState.amount)
async def wrong_amount(message: Message) -> None:
    await message.answer(
        text='Некорректный ввод\nТребуется ввести сумму - числовое значение с точкой или без',
        reply_markup=kb.cancel,
    )


@router.callback_query(F.data == 'confirm-add-order')
async def confirm_add_order(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    user = await db.user.get(
        user_id=call.from_user.id,
    )
    order = await db.order.create(
        bank=OrderBank(data['bank']),
        card=data['card'],
        amount=data['amount'],
        operator=user,
    )
    await distribute_order(order)

    await state.clear()
    await call.message.edit_text(
        text=f'Заявка <b>{order.title}</b> создана',
        reply_markup=kb.in_menu,
    )
