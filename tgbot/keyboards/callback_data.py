from aiogram.filters.callback_data import CallbackData


class CurrencyGiveCallback(CallbackData, prefix='currency_give'):
    currency_id: str


class CurrencyGetCallback(CallbackData, prefix='currency_get'):
    currency_id: str


class MakeDeal(CallbackData, prefix='deal'):
    direction_id: str
    method: str


class SelectedDirectionsCallback(CallbackData, prefix='selected'):
    direction_id: str


class CancelBidCallback(CallbackData, prefix='cancel_bid'):
    id: int
    method: str


class HistoryCallback(CallbackData, prefix='history'):
    current_idx: int


class ShowHistoryExchange(CallbackData, prefix='show_history'):
    id: int


class SelectedDirectionsExchange(CallbackData, prefix='selected_directions'):
    current_idx: int


class ShowSelectedDir(CallbackData, prefix='show_s_d'):
    id: int


class ShowReserve(CallbackData, prefix='r'):
    id: str
    name: str
