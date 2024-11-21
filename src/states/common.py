from aiogram.fsm.state import State, StatesGroup


class AddParticipantState(StatesGroup):
    input = State()
