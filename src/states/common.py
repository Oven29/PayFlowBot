from aiogram.fsm.state import State, StatesGroup


class AddParticipantState(StatesGroup):
    input = State()


class EditOrderState(StatesGroup):
    uid = State()
    amount = State()
    card = State()
