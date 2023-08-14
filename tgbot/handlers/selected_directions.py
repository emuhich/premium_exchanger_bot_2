from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold, hcode

from tgbot.config import Config
from tgbot.keyboards.callback_data import ShowSelectedDir, SelectedDirectionsExchange
from tgbot.keyboards.inline import back_to_manu_kb, selected_directions_kb, directions_info_kb, back_to_selected_dir_kb
from tgbot.misc.tools import pagination, format_number
from tgbot.models.db_commands import select_client, get_direction

selected_directions_router = Router()


@selected_directions_router.callback_query(SelectedDirectionsExchange.filter())
async def history(call: CallbackQuery, callback_data: SelectedDirectionsExchange, config: Config):
    await call.answer()
    user = await select_client(call.message.chat.id)
    directions = user.selected.all()
    good_directions = await config.misc.exchanger.get_directions()
    good_directions_id = [i['direction_id'] for i in good_directions]
    directions = [i for i in directions if i.direction_id in good_directions_id]
    if not directions:
        return await call.message.edit_text(text='\n'.join([
            f'Вы пока не добавили избранные направления'
        ]), reply_markup=await back_to_manu_kb())

    categories, current_idx, current_page = await pagination(directions, callback_data.current_idx, 10)
    try:
        await call.message.edit_text('Выберите направление 👇',
                                     reply_markup=await selected_directions_kb(categories, current_idx, current_page))
    except TelegramBadRequest:
        pass


@selected_directions_router.callback_query(ShowSelectedDir.filter())
async def show_history(call: CallbackQuery, callback_data: ShowSelectedDir, config: Config):
    direction_db = await get_direction(callback_data.id)
    direction = await config.misc.exchanger.get_direction(direction_db.direction_id)

    await call.message.edit_text(text='\n'.join([
        f'{hbold(direction_db.name)}\n',
        f'{hbold("Курс:")} {await format_number(direction["course_give"])} {direction["currency_code_give"]} = '
        f'{await format_number(direction["course_get"])} {direction["currency_code_get"]}',
        f'{hbold("Резерв: ")} {hcode(await format_number(direction["reserve"]))} {direction["currency_code_get"]}',
        f'{hbold("Мин. сумма:")} {hcode(direction["min_give"])} {direction["currency_code_give"]}',
        f'{hbold("Макс. сумма:")} {hcode(direction["max_give"])} {direction["currency_code_give"]}',
    ]), reply_markup=await back_to_selected_dir_kb(direction['id']))
