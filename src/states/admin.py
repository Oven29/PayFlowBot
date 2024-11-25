from aiogram.fsm.state import State, StatesGroup


class EditParticipantState(StatesGroup):
    commission = State()
    balance = State()
