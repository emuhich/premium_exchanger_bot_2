import math
from typing import Union, Optional

from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, InputFile, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, ForceReply
from bs4 import BeautifulSoup
from pydantic import ValidationError


async def one_message_editor(
        event: CallbackQuery | Message,
        text: Optional[str] = None,
        reply_markup: Optional[
            Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
        photo: Union[InputFile, str] = None,
        document: Union[InputFile, str] = None,
        video: Union[InputFile, str] = None,
        parse_mode: Optional[str] = 'HTML',
        disable_web_page_preview: bool = False,
):
    """
        Этот метод служит для автоматического изменения/удаления предыдущего сообщения для того чтобы не захламлять
        чат и был вид одного сообщения. Можно отправлять Текст, Фото, Видео, Документы.

        :param event: Объект, который принимает handler, может быть CallbackQuery или Message
        :param text: Текст сообщения либо описание под медиа
        :param reply_markup: Клавиатура отправляемая с сообщением
        :param photo: Передавайте если хотите отправить фото
        :param document: Передавайте если хотите отправить документ
        :param video: Передавайте если хотите отправить видео
        :param parse_mode: Передавайте если хотите изменить parse_mode. Default = HTML
        :param disable_web_page_preview: Показывать преью сайта в сообщении или нет. Default = False
    """
    content_type = [ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]

    if isinstance(event, CallbackQuery) and not photo and not video and not document \
            and not event.message.content_type in content_type:
        try:
            await event.message.edit_text(text=text, parse_mode=parse_mode, reply_markup=reply_markup,
                                          disable_web_page_preview=disable_web_page_preview)
        except TelegramBadRequest:
            try:
                await event.message.delete()
            except TelegramBadRequest:
                pass
            await event.message.answer(text=text, parse_mode=parse_mode, reply_markup=reply_markup,
                                       disable_web_page_preview=disable_web_page_preview)
        except ValidationError:
            try:
                await event.message.delete()
            except TelegramBadRequest:
                pass
            await event.message.answer(text=text, parse_mode=parse_mode, reply_markup=reply_markup,
                                       disable_web_page_preview=disable_web_page_preview)
    else:
        if isinstance(event, CallbackQuery):
            event = event.message
        try:
            await event.delete()
        except TelegramBadRequest:
            pass
        if photo:
            await event.answer_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode=parse_mode,
                                     disable_web_page_preview=disable_web_page_preview)
        elif video:
            await event.answer_video(video=video, caption=text, reply_markup=reply_markup, parse_mode=parse_mode,
                                     disable_web_page_preview=disable_web_page_preview)
        elif document:
            await event.answer_document(document=document, caption=text, reply_markup=reply_markup,
                                        parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
        else:
            await event.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode,
                               disable_web_page_preview=disable_web_page_preview)


async def format_number(number):
    return '{0:,}'.format(float(number)).replace(',', ' ')


async def round_amount(currency_id, amount):
    # Округление рубли
    if currency_id in ['4', '54', '13', '14', '15', '42', '57', '59', '66', '71', '72', '73', '74', '76', '76', '9',
                       '78', '77', '91', '87', '106', '107', '108']:
        return int(amount)
    elif currency_id in ['53', '51', '50', '89', '96']:
        return round(amount, 6)
    else:
        return round(amount, 2)


async def pagination(elements, current_index, page_size):
    # Определяем границы среза
    start_index = current_index
    end_index = current_index + page_size

    # Корректируем границы среза, если они выходят за пределы списка
    if start_index <= 0:
        current_index = 0
        start_index = 0
        end_index = page_size
    elif start_index >= len(elements):  # Если ушли за пределы списка вправо
        end_index = current_index
        start_index = current_index - page_size
        current_index = start_index

    current_page = current_index // page_size + 1  # Получаем текущую страницу
    count_page = math.ceil(len(elements) / page_size)  # Получаем последнюю страницу
    return elements[start_index:end_index], current_index, f"{current_page}/{count_page}"


async def clear_text(text):
    soup = BeautifulSoup(text, 'lxml')  # Удаление новых строк
    return soup.text


async def get_status_info(status):
    status_dict = {
        'coldnew': "Заявка ожидает проверки",
        'new': "Создана",
        'cancel': "Отменена пользователем",
        'delete': "Удалена",
        'techpay': "Пользователь перешел в раздел оплаты",
        'payed': "Оплачена",
        'coldpay': "Ожидание подтверждения оплаты",
        'partpay': "Частично оплачена",
        'realpay': "Оплачена",
        'verify': "На проверке",
        'mercherror': "Ошибка продавца",
        'error': "Ошибка заявки",
        'payouterror': "Ошибка автоматической выплаты",
        'scrpayerror': "Ошибка автоматической выплаты",
        'coldsuccess': "Ожидание подтверждения автоматической оплаты",
        'partpayout': "Частично выплачена",
        'success': "Успешно завершена",
    }
    return status_dict.get(status)
