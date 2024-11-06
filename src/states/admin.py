from aiogram.fsm.state import State, StatesGroup


class EditOrderState(StatesGroup):
    amount = State()
    card = State()
