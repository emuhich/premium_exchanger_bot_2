from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.callback_data import CurrencyGiveCallback, CurrencyGetCallback, MakeDeal, \
    SelectedDirectionsCallback, CancelBidCallback, HistoryCallback, ShowHistoryExchange, SelectedDirectionsExchange, \
    ShowSelectedDir, ShowReserve


async def menu_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="♻️Новый обмен♻️", callback_data="exchange")
    keyboard.button(text="🗄История обменов 🗄", callback_data=HistoryCallback(current_idx=0))
    keyboard.button(text="📎 Избранные направления 📎", callback_data=SelectedDirectionsExchange(current_idx=0))
    # keyboard.button(text="💰Резервы💰", callback_data="reserves")
    # keyboard.button(text="☎️ Контакты ☎️", callback_data="contact")
    keyboard.button(text="🆘 Поддержка 🆘", callback_data="support")
    # keyboard.button(text="📝 Правила 📝", callback_data="rules")
    # keyboard.button(text="🕵️‍♂️ AML/KYC политика 🕵️‍♂️", callback_data="policy")
    keyboard.adjust(1)
    return keyboard.as_markup()


async def currencies_give_kb(currencies):
    keyboard = InlineKeyboardBuilder()
    for currency in currencies:
        keyboard.button(text=currencies[currency], callback_data=CurrencyGiveCallback(currency_id=currency))
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_manu"))
    return keyboard.as_markup()


async def currencies_get_kb(currencies):
    keyboard = InlineKeyboardBuilder()
    for currency in currencies:
        keyboard.button(text=currencies[currency], callback_data=CurrencyGetCallback(currency_id=currency))
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="exchange"))
    return keyboard.as_markup()


async def directions_info_kb(currency_id, user, direction_id, cash_status, url):
    keyboard = InlineKeyboardBuilder()
    selected = user.selected.filter(direction_id=direction_id)
    if cash_status:
        keyboard.button(text="Оформить сделку на сайте", url=url)
    else:
        keyboard.button(text="Оформить сделку", callback_data=MakeDeal(
            direction_id=direction_id,
            method='give'
        ))
    if not selected and not cash_status:
        keyboard.button(text="Добавить в избранное",
                        callback_data=SelectedDirectionsCallback(direction_id=direction_id))
    keyboard.button(text="🔙 Назад", callback_data=CurrencyGiveCallback(currency_id=currency_id))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def swap_amount_method_kb(method, direction_id, currency_id):
    keyboard = InlineKeyboardBuilder()
    if method == 'give':
        keyboard.button(text="Ввести сумму получаю", callback_data=MakeDeal(
            direction_id=direction_id,
            method='get'
        ))
    else:
        keyboard.button(text="Ввести сумму отдаю", callback_data=MakeDeal(
            direction_id=direction_id,
            method='give'
        ))
    keyboard.button(text="🔙 Назад", callback_data=CurrencyGetCallback(currency_id=currency_id))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def back_to_direction(currency_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔙 Назад", callback_data=CurrencyGetCallback(currency_id=currency_id))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def valid_exchange_kb(currency_get_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Подтвердить", callback_data="confirm_exchange")
    keyboard.button(text="❌ Отмена", callback_data=CurrencyGetCallback(currency_id=currency_get_id))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def back_to_direction_create(currency_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔙 Вернуться к заявке", callback_data=CurrencyGetCallback(currency_id=currency_id))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def cancel_bid_kb(exchange_id, url):
    keyboard = InlineKeyboardBuilder()
    if url:
        keyboard.button(text='💸 Оплатить по ссылке', url=url)
    else:
        keyboard.button(text='✅ Оплатил заявку', callback_data=CancelBidCallback(
            id=exchange_id,
            method='pay'
        ))
    keyboard.button(text="❌ Отменить заявку", callback_data=CancelBidCallback(
        id=exchange_id,
        method='cancel'
    ))
    keyboard.button(text="🔙 Вернуться в главное меню", callback_data="back_to_manu")
    keyboard.adjust(1)
    return keyboard.as_markup()


async def back_to_manu_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔙 Вернуться в главное меню", callback_data="back_to_manu")
    keyboard.adjust(1)
    return keyboard.as_markup()


async def support_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='🆘 Обратиться в поддержку 🆘', url='https://t.me/FastExchange_Support')
    keyboard.button(text="🔙 Вернуться в главное меню", callback_data="back_to_manu")
    keyboard.adjust(1)
    return keyboard.as_markup()


async def history_exchange_kb(objects, current_idx, current_page):
    keyboard = InlineKeyboardBuilder()
    for i in objects:
        keyboard.button(text=f'{i.name}|{i.created.strftime("%d.%m.%Y %H:%M")}',
                        callback_data=ShowHistoryExchange(id=i.pk))
    keyboard.adjust(1)
    next_b = InlineKeyboardButton(text=">", callback_data=HistoryCallback(current_idx=current_idx + 5).pack())
    middle_b = InlineKeyboardButton(text=current_page,
                                    callback_data=HistoryCallback(current_idx=current_idx).pack())
    back_b = InlineKeyboardButton(text="<", callback_data=HistoryCallback(current_idx=current_idx - 5).pack())
    keyboard.row(back_b, middle_b, next_b)
    keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_manu"))
    return keyboard.as_markup()


async def back_to_history_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔙 Назад", callback_data=HistoryCallback(current_idx=0))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def selected_directions_kb(objects, current_idx, current_page):
    keyboard = InlineKeyboardBuilder()
    for i in objects:
        keyboard.button(text=i.name, callback_data=ShowSelectedDir(id=i.pk))
    keyboard.adjust(1)
    next_b = InlineKeyboardButton(text=">",
                                  callback_data=SelectedDirectionsExchange(current_idx=current_idx + 5).pack())
    middle_b = InlineKeyboardButton(text=current_page,
                                    callback_data=SelectedDirectionsExchange(current_idx=current_idx).pack())
    back_b = InlineKeyboardButton(text="<",
                                  callback_data=SelectedDirectionsExchange(current_idx=current_idx - 5).pack())
    keyboard.row(back_b, middle_b, next_b)
    keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_manu"))
    return keyboard.as_markup()


async def back_to_selected_dir_kb(direction_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Оформить сделку", callback_data=MakeDeal(
        direction_id=direction_id,
        method='give'
    ))
    keyboard.button(text="🔙 Назад", callback_data=SelectedDirectionsExchange(current_idx=0))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def reserves_kb(reserves):
    keyboard = InlineKeyboardBuilder()
    for reserve in reserves:
        keyboard.button(text=reserves[reserve], callback_data=ShowReserve(id=reserve, name=reserves[reserve]))
    keyboard.adjust(3)
    keyboard.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_manu"))
    return keyboard.as_markup()


async def back_to_reserves_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔙 Назад", callback_data="reserves")
    keyboard.adjust(1)
    return keyboard.as_markup()
