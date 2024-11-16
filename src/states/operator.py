from aiogram.fsm.state import State, StatesGroup


class AddOrderState(StatesGroup):
    uid = State()
    card = State()
    amount = State()
