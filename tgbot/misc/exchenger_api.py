import aiohttp
from aiogram.utils.markdown import hcode
from loguru import logger

from tgbot.misc.tools import good_direction_id


class PremiumExchanger:
    def __init__(self, api_login: str, api_key: str) -> None:
        self.host = 'cripthub.ru'
        self.headers = {
            'API-LOGIN': api_login,
            'API-KEY': api_key,
            'API-LANG': 'ru_RU'
        }

    async def get_request(self, url: str, params: dict = None):
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, params=params, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.error(f'Ошибка в запросе: {resp.text()}')
                return None

    async def get_directions(self):
        url = f'https://{self.host}/api/userapi/v1/get_directions'
        response = await self.get_request(url)
        if response:
            return response['data']
        return None

    async def get_direction_currencies(self):
        url = f'https://{self.host}/api/userapi/v1/get_direction_currencies'
        response = await self.get_request(url)
        if response:
            return response['data']
        return None

    async def get_direction(self, direction_id):
        url = f'https://{self.host}/api/userapi/v1/get_direction'
        payload = {
            'direction_id': direction_id
        }
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, data=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return (await resp.json())['data']
                logger.error(f'Ошибка в запросе: {resp.text()}')
                return None

    async def unique_received_currencies(self):
        directions = await self.get_directions()
        unique_get_currencies = {}
        for direction in directions:
            if not direction['currency_get_id'] in unique_get_currencies:
                unique_get_currencies[direction['currency_get_id']] = direction['currency_get_title']
        return unique_get_currencies

    async def get_reserve(self, currency_get_id):
        directions = await self.get_directions()
        direction_id = None
        for direction in directions:
            if direction['currency_get_id'] == currency_get_id:
                direction_id = direction['direction_id']

        if not direction_id:
            return 0

        direction = await self.get_direction(direction_id)
        return f'{hcode(direction["reserve"])} {direction["currency_code_get"]}'

    async def unique_give_currencies(self):
        directions = await self.get_directions()
        good_direction = await good_direction_id()
        directions = [i for i in directions if i['direction_id'] in good_direction]
        currencies = {}
        for direction in directions:
            if not direction['currency_give_id'] in currencies:
                currencies[direction['currency_give_id']] = direction['currency_give_title']
        return currencies

    async def get_received_currencies(self, currency_give_id):
        directions = await self.get_directions()
        good_direction = await good_direction_id()
        directions = [i for i in directions if i['direction_id'] in good_direction]
        currencies = {}
        for direction in directions:
            if direction['currency_give_id'] == currency_give_id:
                currencies[direction['currency_get_id']] = direction['currency_get_title']
        return currencies

    async def get_direction_by_currency(self, currency_get_id, currency_give_id):
        directions = await self.get_directions()
        direction_id = None
        for i in directions:
            if i['currency_give_id'] == currency_give_id and i['currency_get_id'] == currency_get_id:
                direction_id = i['direction_id']
        if direction_id:
            return await self.get_direction(direction_id)
        return None

    async def get_full_name_currency(self, type_currency, currency_id):
        url = f'https://{self.host}/api/userapi/v1/get_direction_currencies'
        response = await self.get_request(url)
        if response:
            currencies = response['data'][type_currency]
            for currency in currencies:
                if currency['id'] == currency_id:
                    return currency['title']
        return None

    async def create_bid(self, direction_id, amount_give, email, get_field, amount_method):
        if amount_method == 'give':
            calc_action = 1
        else:
            calc_action = 2
        payload = {
            'direction_id': direction_id,
            'calc_amount': amount_give,
            'status': 'new',
            'calc_action': calc_action,
            'cf1': email,
        }
        for i in get_field:
            payload[i] = get_field[i]["value"]
        url = f'https://{self.host}/api/userapi/v1/create_bid'
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, data=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.error(f'Ошибка в запросе: {resp.text()}')
                return None

    async def cancel_exchange(self, exchange_hash):
        payload = {
            'hash': exchange_hash,
        }
        url = f'https://{self.host}/api/userapi/v1/cancel_bid'
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, data=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return True
                logger.error(f'Ошибка в запросе: {resp.text()}')
                return False

    async def pay_exchange(self, exchange_hash):
        payload = {
            'hash': exchange_hash,
        }
        url = f'https://{self.host}/api/userapi/v1/pay_bid'
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, data=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return True
                logger.error(f'Ошибка в запросе: {resp.text()}')
                return False

    async def get_exchange(self, exchange_id):
        payload = {
            'id': exchange_id,
        }
        url = f'https://{self.host}/api/userapi/v1/get_exchanges'
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, data=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return (await resp.json())['data']['items'][0]
                logger.error(f'Ошибка в запросе: {resp.text()}')
                return False

    async def get_calc(self, direction_id, amount, amount_method):
        if amount_method == 'give':
            calc_action = 1
        else:
            calc_action = 2
        payload = {
            'direction_id': direction_id,
            'calc_amount': amount,
            'calc_action': calc_action,
        }
        url = f'https://{self.host}/api/userapi/v1/get_calc'
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, data=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return (await resp.json())['data']
                logger.error(f'Ошибка в запросе: {resp.text()}')
                return False
