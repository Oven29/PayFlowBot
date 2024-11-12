from aiogram.fsm.state import State, StatesGroup


class RejectOrderState(StatesGroup):
    reason = State()


class CancelOrderState(StatesGroup):
    reason = State()


class DisputeOrderState(StatesGroup):
    reason = State()


class ConfirmOrderState(StatesGroup):
    check = State()
