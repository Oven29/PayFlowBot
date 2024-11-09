from aiogram.fsm.state import State, StatesGroup


class AddOrderState(StatesGroup):
    card = State()
    amount = State()
