import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold, hcode, hlink
from loguru import logger

from tgbot.config import Config
from tgbot.keyboards.callback_data import CurrencyGiveCallback, CurrencyGetCallback, SelectedDirectionsCallback, \
    MakeDeal, CancelBidCallback
from tgbot.keyboards.inline import currencies_give_kb, currencies_get_kb, directions_info_kb, back_to_direction, \
    valid_exchange_kb, back_to_direction_create, back_to_manu_kb, cancel_bid_kb, swap_amount_method_kb
from tgbot.misc.states import States
from tgbot.misc.tools import format_number, round_amount, clear_text
from tgbot.models.db_commands import select_client, create_selected_directions, create_exchange_db, get_exchange

exchange_router = Router()


@exchange_router.callback_query(F.data == "exchange")
async def exchange_give(call: CallbackQuery, config: Config):
    currencies = await config.misc.exchanger.unique_give_currencies()
    await call.message.edit_text(text="Выберете валюту которую хотите отдать 👇",
                                 reply_markup=await currencies_give_kb(currencies))


@exchange_router.callback_query(CurrencyGiveCallback.filter())
async def exchange_get(call: CallbackQuery, callback_data: CurrencyGiveCallback, config: Config, state: FSMContext):
    await state.update_data(currency_give_id=callback_data.currency_id)
    currencies = await config.misc.exchanger.get_received_currencies(callback_data.currency_id)
    await call.message.edit_text(text="Выберете валюту которую хотите получить 👇",
                                 reply_markup=await currencies_get_kb(currencies))


@exchange_router.callback_query(CurrencyGetCallback.filter())
async def show_direction(call: CallbackQuery, callback_data: CurrencyGetCallback, config: Config, state: FSMContext):
    await state.set_state(None)
    data = await state.get_data()
    currency_give_id = data.get('currency_give_id')
    await state.update_data(currency_get_id=callback_data.currency_id)
    direction = await config.misc.exchanger.get_direction_by_currency(callback_data.currency_id, currency_give_id)
    await state.update_data(direction_id=direction['id'])

    get_name = await config.misc.exchanger.get_full_name_currency('get', callback_data.currency_id)
    give_name = await config.misc.exchanger.get_full_name_currency('give', currency_give_id)

    user = await select_client(call.message.chat.id)

    cash_ids = ['57', '103', '20', '88', '100']

    cash_status = False
    if callback_data.currency_id in cash_ids or currency_give_id in cash_ids:
        cash_status = True

    await call.message.edit_text(text='\n'.join([
        f'{hbold(f"{give_name} ➡️ {get_name}")}\n',
        f'{hbold("Курс:")} {await format_number(direction["course_give"])} {direction["currency_code_give"]} = '
        f'{await format_number(direction["course_get"])} {direction["currency_code_get"]}',
        f'{hbold("Резерв: ")} {hcode(await format_number(direction["reserve"]))} {direction["currency_code_get"]}',
        f'{hbold("Мин. сумма:")} {hcode(direction["min_give"])} {direction["currency_code_give"]}',
        f'{hbold("Макс. сумма:")} {hcode(direction["max_give"])} {direction["currency_code_give"]}',
    ]), reply_markup=await directions_info_kb(currency_give_id, user, direction['id'], cash_status, direction['url']))


@exchange_router.callback_query(SelectedDirectionsCallback.filter())
async def select_direction(call: CallbackQuery, callback_data: SelectedDirectionsCallback, config: Config,
                           state: FSMContext):
    user = await select_client(call.message.chat.id)
    directions = await config.misc.exchanger.get_directions()
    direction = [i for i in directions if i['direction_id'] == callback_data.direction_id][0]
    await create_selected_directions(user, callback_data.direction_id, f'{direction["currency_give_title"]} ➡️ '
                                                                       f'{direction["currency_get_title"]}')
    data = await state.get_data()
    callback_data = CurrencyGetCallback(currency_id=data.get('currency_get_id'))
    await call.answer(text='✅ Направление добавлено в избранное')
    await show_direction(call, callback_data, config, state)


@exchange_router.callback_query(MakeDeal.filter())
async def amount_exchange(call: CallbackQuery, callback_data: MakeDeal, state: FSMContext, config: Config):
    data = await state.get_data()
    direction = await config.misc.exchanger.get_direction(callback_data.direction_id)
    await state.set_state(States.give_amount)
    await state.update_data(amount_method=callback_data.method)
    kb = await swap_amount_method_kb(callback_data.method, callback_data.direction_id, data.get('currency_get_id'))
    if callback_data.method == 'give':
        currency_name = direction["currency_code_give"]
        await call.message.edit_text(text='\n'.join([
            f'{hbold(f"Введите сумму в {currency_name}")} которую хотите отдать',
            f'{hbold("Мин. сумма:")} {hcode(direction["min_give"])} {currency_name}',
            f'{hbold("Макс. сумма:")} {hcode(direction["max_give"])} {currency_name}',
        ]), reply_markup=kb)
    else:
        currency_name = direction['currency_code_get']
        await call.message.edit_text(text='\n'.join([
            f'{hbold(f"Введите сумму в {currency_name}")} которую хотите отдать',
            f'{hbold("Мин. сумма:")} {hcode(direction["min_get"])} {currency_name}',
            f'{hbold("Макс. сумма:")} {hcode(direction["max_get"])} {currency_name}',
        ]), reply_markup=kb)


@exchange_router.message(States.give_amount)
async def valid_amount(message: Message, state: FSMContext, config: Config):
    data = await state.get_data()
    amount_method = data.get('amount_method')
    direction = await config.misc.exchanger.get_direction(data.get("direction_id"))

    try:
        amount = float(message.text.replace(' ', ''))
    except Exception:
        return await message.answer('Введенная сумма должна быть числом, введите новое число под этим сообщением',
                                    reply_markup=await back_to_direction(data.get('currency_get_id')))
    if amount_method == 'give':
        min_sum = direction["min_give"]
        max_sum = direction["max_give"]
    else:
        min_sum = direction["min_get"]
        max_sum = direction["max_get"]
    if amount < float(min_sum):
        return await message.answer(
            f'Введенная сумма должна быть больше {hcode(await format_number(min_sum))}, '
            'введите новое число под этим сообщением',
            reply_markup=await back_to_direction(data.get('currency_get_id')))
    elif amount > float(max_sum):
        return await message.answer(
            f'Введенная сумма должна быть не больше {hcode(await format_number(max_sum))}, '
            'введите новое число под этим сообщением',
            reply_markup=await back_to_direction(data.get('currency_get_id')))

    await state.update_data(amount=amount)
    await state.set_state(States.account)
    get_field = {}
    for i in direction['get_fields']:
        tooltip = direction['get_fields'][i].get('tooltip')
        if not tooltip:
            tooltip = 'Укажите счет на который хотите получить средства'
        get_field[i] = {
            'label': direction['get_fields'][i]['label'],
            'tooltip': tooltip,
            'value': None
        }
    for i in direction['give_fields']:
        tooltip = direction['give_fields'][i].get('tooltip')
        if not tooltip:
            tooltip = 'Укажите счет на который хотите получить средства'
        get_field[i] = {
            'label': direction['give_fields'][i]['label'],
            'tooltip': tooltip,
            'value': None
        }
    await state.update_data(get_field=get_field)
    first_field = list(get_field)[0]
    await message.answer(text=f'{get_field[first_field]["tooltip"]}',
                         reply_markup=await back_to_direction(data.get('currency_get_id')))


@exchange_router.message(States.account)
async def valid_exchange(message: Message, state: FSMContext):
    data = await state.get_data()
    get_field = data.get('get_field')
    for i in get_field:
        if get_field[i]['value'] is None:
            get_field[i]['value'] = message.text
            break

    await state.update_data(get_field=get_field)
    check_field = [i for i in get_field if get_field[i]['value'] is None]
    if check_field:
        field = check_field[0]
        return await message.answer(text=f'{get_field[field]["tooltip"]}',
                                    reply_markup=await back_to_direction(data.get('currency_get_id')))
    await state.set_state(States.email)
    await message.answer(text='Укажите свою почту ниже',
                         reply_markup=await back_to_direction(data.get('currency_get_id')))


@exchange_router.message(States.email)
async def valid_email(message: Message, state: FSMContext, config: Config):
    data = await state.get_data()
    get_field = data.get('get_field')
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, message.text):
        return message.answer(text='Кажется вы ошиблись, введите новую почту ниже',
                              reply_markup=await back_to_direction(data.get('currency_get_id')))
    await state.update_data(email=message.text)
    direction = await config.misc.exchanger.get_direction(data.get("direction_id"))

    # amount_give = data.get('amount')

    amount_calc = (await config.misc.exchanger.get_calc(data.get("direction_id"), data.get('amount'), data.get('amount_method')))

    # amount_get = await round_amount(data.get('currency_get_id'), float(amount_get))

    get_name = await config.misc.exchanger.get_full_name_currency('get', data.get('currency_get_id'))
    give_name = await config.misc.exchanger.get_full_name_currency('give', data.get('currency_give_id'))
    text = [
        hbold('Заявка на обмен\n'),
        f'{hbold(f"{give_name} ➡️ {get_name}")}\n',
        f'{hbold("Курс:")} {await format_number(direction["course_give"])} {direction["currency_code_give"]} = '
        f'{await format_number(direction["course_get"])} {direction["currency_code_get"]}',
        f'{hbold("Отдаете:")} {hcode(await format_number(amount_calc["sum_give"]))} {direction["currency_code_give"]}',
        f'{hbold("Получаете:")} {hcode(await format_number(amount_calc["sum_get"]))} {direction["currency_code_get"]}',
        f'{hbold("Почта: ")} {hcode(message.text)}'
    ]
    for i in get_field:
        text.append(f'{hbold(get_field[i]["label"])}: {hcode(get_field[i]["value"])}')

    await message.answer(text='\n'.join(text), reply_markup=await valid_exchange_kb(data.get('currency_get_id')))


@exchange_router.callback_query(F.data == "confirm_exchange")
async def create_exchange(call: CallbackQuery, config: Config, state: FSMContext):
    await state.set_state(None)
    user = await select_client(call.message.chat.id)
    data = await state.get_data()
    response = await config.misc.exchanger.create_bid(
        data.get("direction_id"), data.get('amount'), data.get('email'), data.get('get_field'), data.get('amount_method'))
    if response['error'] == "0":
        exchange = await create_exchange_db(user, f'{response["data"]["psys_give"]} ➡️ {response["data"]["psys_get"]}',
                                            response["data"]["id"])

        if data.get("direction_id") not in ['1009', '1011', '1008', '1005', '1004', '1003', '119']:
            text = [(await clear_text(response["data"]["api_actions"]["instruction"]))]
            link = None
        else:
            direction = await config.misc.exchanger.get_direction(data.get("direction_id"))
            timeline_text = direction['info'].get('timeline_text')

            link = response["data"]["api_actions"]["pay"]
            text = []
            if timeline_text:
                text.append((await clear_text(timeline_text)))
            else:
                text.append((await clear_text(response["data"]["api_actions"]["instruction"])))

            if 'address' in response["data"]["api_actions"]:
                text.append(
                    f'\nПереведите {hcode(response["data"]["api_actions"]["pay_amount"])} {response["data"]["currency_code_give"]} на счет: '
                    f'{hcode(response["data"]["api_actions"]["address"])}')
        return await call.message.edit_text(text='\n'.join(text), reply_markup=await cancel_bid_kb(
            exchange_id=exchange.pk, url=link))
    logger.error(f'Ошибка про создании заявки: {response["error_fields"]}')
    await call.message.edit_text(text='❌ Произошла ошибка, вы ввели некорректные данные, попробуйте повторить',
                                 reply_markup=await back_to_direction_create(data.get('currency_get_id')))


@exchange_router.callback_query(CancelBidCallback.filter())
async def cancel_bid(call: CallbackQuery, callback_data: CancelBidCallback, config: Config):
    exchange = await get_exchange(callback_data.id)
    exchange_from_api = await config.misc.exchanger.get_exchange(exchange.exchange_id)
    if callback_data.method == 'cancel':
        exchange.status = 'cancel'
        await config.misc.exchanger.cancel_exchange(exchange_from_api['hash'])
        await call.message.edit_text(text='\n'.join([
            f'Заявка отменена'
        ]), reply_markup=await back_to_manu_kb())
    else:
        exchange.status = 'payed'
        await config.misc.exchanger.pay_exchange(exchange_from_api['hash'])
        await call.message.edit_text(text='\n'.join([
            f'✅ Статус заявки изменен, ожидайте поступления средств'
        ]), reply_markup=await back_to_manu_kb())
    exchange.save()
