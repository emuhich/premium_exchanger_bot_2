import random
import string
from io import BytesIO

from aiogram import Router, F, exceptions
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from captcha.image import ImageCaptcha

from tgbot.keyboards.inline import menu_kb, back_to_manu_kb, support_kb
from tgbot.misc.states import States
from tgbot.models.db_commands import select_client, create_client

user_router = Router()


@user_router.message(Command(commands=["start"]))
async def user_start(message: Message, state: FSMContext):
    await state.set_state(None)
    user = await select_client(message.chat.id)
    if not user:
        captcha_code = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        image_captcha = ImageCaptcha(width=280, height=90)
        image = image_captcha.generate_image(captcha_code)
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        await state.update_data(captcha_code=captcha_code)
        await state.set_state(States.captcha_code)
        return await message.answer_photo(photo=BufferedInputFile(image_io.getvalue(), filename='captcha.png'),
                                          caption='Введите код с картинки ниже 👇')
    await message.answer(text="Выберете пункт меню 👇", reply_markup=await menu_kb())


@user_router.message(States.captcha_code, F.text)
async def check_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    captcha_code = data.get('captcha_code')
    if message.text.lower() != captcha_code.lower():
        captcha_code = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        image_captcha = ImageCaptcha(width=280, height=90)
        image = image_captcha.generate_image(captcha_code)
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        await state.update_data(captcha_code=captcha_code)
        return await message.answer_photo(photo=BufferedInputFile(image_io.getvalue(), filename='captcha.png'),
                                          caption='❌ Ошибка, неверный код, введите новый код ниже 👇')
    await create_client(message.from_user.username, message.chat.id, message.from_user.url,
                        message.from_user.full_name)
    await message.answer(text="Выберете пункт меню 👇", reply_markup=await menu_kb())


@user_router.message(Command(commands=["support"]))
@user_router.callback_query(F.data == "support")
async def support(call: CallbackQuery | Message, state: FSMContext):
    await state.set_state(None)
    text = [
        f'Обратиться в поддержку можно по кнопке ниже  👇'
    ]
    if isinstance(call, CallbackQuery):
        await call.message.edit_text(text='\n'.join(text), reply_markup=await support_kb())
    elif isinstance(call, Message):
        await call.answer(text='\n'.join(text), reply_markup=await support_kb())


@user_router.callback_query(F.data == "contact")
async def contact(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await call.message.edit_text(text='\n'.join([
        f'Наши контакты:\n',
        f'Электронная почта: info@cripthub.ru',
        f'Официальный сайт: cripthub.ru\n',
        f'Обратиться в поддержку можно по кнопке ниже  👇'
    ]), reply_markup=await support_kb(), disable_web_page_preview=True)


@user_router.callback_query(F.data == "back_to_manu")
async def back_to_manu(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except (exceptions.TelegramAPIError, exceptions.TelegramBadRequest):
        pass
    await user_start(call.message, state)


@user_router.callback_query(F.data == "contact")
async def contact(call: CallbackQuery):
    await call.message.edit_text(text='Контакты', reply_markup=await back_to_manu_kb())
