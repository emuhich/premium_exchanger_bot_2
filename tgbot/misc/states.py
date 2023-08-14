from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    give_amount = State()
    account = State()
    email = State()
