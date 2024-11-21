from aiogram.fsm.state import State, StatesGroup


class EditOrderState(StatesGroup):
    amount = State()
    card = State()


class EditParticipantState(StatesGroup):
    commission = State()
    balance = State()
