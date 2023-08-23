from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.utils.markdown import hbold

from tgbot.misc.exchenger_api import PremiumExchanger
from tgbot.misc.tools import get_status_info
from tgbot.models.db_commands import get_all_exchangers, get_direction, add_direction


async def check_exchange_status(bot: Bot, exchanger: PremiumExchanger):
    exchanges = await get_all_exchangers()
    for exchange in exchanges:
        try:
            exchange_api_info = await exchanger.get_exchange(exchange.exchange_id)
        except Exception:
            continue
        if exchange.status != exchange_api_info['status']:
            exchange.status = exchange_api_info['status']
            status = await get_status_info(exchange_api_info['status'])
            try:
                await bot.send_message(text='\n'.join([
                    f'Статус заявки №{exchange.exchange_id} изменился на {hbold(status)}'
                ]), chat_id=exchange.user.telegram_id)
            except (TelegramForbiddenError, TelegramBadRequest):
                pass
            exchange.save()


async def parse_direction(exchanger: PremiumExchanger):
    directions = await exchanger.get_directions()
    if not directions:
        return
    count = 0
    for direction in directions:
        check_dir = await get_direction(direction['direction_id'])
        if check_dir:
            continue

        await add_direction(direction['direction_id'], f'{direction["currency_give_title"]} ➡️ '
                                                       f'{direction["currency_get_title"]}')
        count += 1
    return count
