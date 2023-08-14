from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold, hcode

from tgbot.config import Config
from tgbot.keyboards.callback_data import HistoryCallback, ShowHistoryExchange
from tgbot.keyboards.inline import back_to_manu_kb, history_exchange_kb, back_to_history_kb
from tgbot.misc.tools import pagination, format_number, get_status_info
from tgbot.models.db_commands import select_client, get_exchange

exchange_history_router = Router()


@exchange_history_router.callback_query(HistoryCallback.filter())
async def history(call: CallbackQuery, callback_data: HistoryCallback):
    await call.answer()

    user = await select_client(call.message.chat.id)
    exchanges = user.exchanges.all()
    if not exchanges:
        return await call.message.edit_text(text='\n'.join([
            f'Вы пока не создали заявку'
        ]), reply_markup=await back_to_manu_kb())

    categories, current_idx, current_page = await pagination(exchanges, callback_data.current_idx, 10)
    try:
        await call.message.edit_text('Выберите заявку 👇',
                                     reply_markup=await history_exchange_kb(categories, current_idx, current_page))
    except TelegramBadRequest:
        pass


@exchange_history_router.callback_query(ShowHistoryExchange.filter())
async def show_history(call: CallbackQuery, callback_data: ShowHistoryExchange, config: Config):
    exchange = await get_exchange(callback_data.id)
    exchange_from_api = await config.misc.exchanger.get_exchange(exchange.exchange_id)
    status = await get_status_info(exchange_from_api['status'])

    await call.message.edit_text(text='\n'.join([
        f'Заявка №{exchange.exchange_id} {exchange.created.strftime("%d.%m.%Y %H:%M")}\n',
        f'{hbold("Статус:")} {status}',
        f'{hbold("Курс:")} {await format_number(exchange_from_api["course_give"])} {exchange_from_api["currency_code_give"]} = '
        f'{await format_number(exchange_from_api["course_get"])} {exchange_from_api["currency_code_get"]}',
        f'{hbold("Отдаете:")} {hcode(await format_number(exchange_from_api["amount_give"]))} {exchange_from_api["currency_code_give"]}',
        f'{hbold("Получаете:")} {hcode(await format_number(exchange_from_api["amount_get"]))} {exchange_from_api["currency_code_get"]}',
    ]), reply_markup=await back_to_history_kb())
