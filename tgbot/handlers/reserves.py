from aiogram import Router, F
from aiogram.types import CallbackQuery

from tgbot.config import Config
from tgbot.keyboards.callback_data import ShowReserve
from tgbot.keyboards.inline import reserves_kb, back_to_reserves_kb

reserves_router = Router()


@reserves_router.callback_query(F.data == "reserves")
async def show_reserves(call: CallbackQuery, config: Config):
    reserves = await config.misc.exchanger.unique_received_currencies()
    await call.message.edit_text(text='\n'.join([
        f'Выберите валюту по которой хотите узнать резерв 👇'
    ]), reply_markup=await reserves_kb(reserves))


@reserves_router.callback_query(ShowReserve.filter())
async def exchange_get(call: CallbackQuery, callback_data: ShowReserve, config: Config):
    reserve = await config.misc.exchanger.get_reserve(callback_data.id)
    await call.message.edit_text(text='\n'.join([
        f'Резерв для {callback_data.name} = {reserve}'
    ]), reply_markup=await back_to_reserves_kb())
