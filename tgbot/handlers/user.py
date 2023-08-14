from aiogram import Router, F, exceptions
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from tgbot.keyboards.inline import menu_kb, back_to_manu_kb, support_kb
from tgbot.models.db_commands import select_client, create_client

user_router = Router()


@user_router.message(Command(commands=["start"]))
async def user_start(message: Message, state: FSMContext):
    await state.set_state(None)
    user = await select_client(message.chat.id)
    if not user:
        await create_client(message.from_user.username, message.chat.id, message.from_user.url,
                            message.from_user.full_name)
    await message.answer(text="Выберете пункт меню 👇", reply_markup=await menu_kb())


@user_router.message(Command(commands=["rules"]))
@user_router.callback_query(F.data == "rules")
async def guarantees(call: CallbackQuery | Message, state: FSMContext):
    document = FSInputFile("Правила.pdf")
    await state.set_state(None)
    if isinstance(call, CallbackQuery):
        await call.message.delete()
        await call.message.answer_document(document=document, reply_markup=await back_to_manu_kb())
    elif isinstance(call, Message):
        await call.delete()
        await call.answer_document(document=document, reply_markup=await back_to_manu_kb())


@user_router.message(Command(commands=["policy"]))
@user_router.callback_query(F.data == "policy")
async def rules(call: CallbackQuery | Message, state: FSMContext):
    await state.set_state(None)
    text = [
        'Дата вступления в силу: 23.10.2022 года.\n',
        f'Политика KYT (Знай свою транзакцию) направлена ​​на идентификацию клиента сделки в случае прецедента, '
        f'когда у Сервиса есть разумные подозрения в том, что Клиент использует Cripthub.ru не по назначению.\n',
        f'Такой прецедент может возникнуть, если Сервис подозревает Клиента в незаконных действиях, которые могут быть '
        f'квалифицированы как отмывание или попытка отмывания цифровых активов, полученных '
        f'неправомерным путем или средства имеют откровенно криминальное происхождение. Для этих целей Сервис '
        f'вправе использовать любую законную информацию, сторонние средства анализа происхождения цифровых активов, '
        f'а также собственные разработки скрининговой системы.\n',
        f'▪️ Обменный пункт не принимает криптовалюту с высоким риском, отправленные с DarkMarket площадок и миксеров.'
        f'▪️ Возврат криптовалюты высоким риском производится только на кошелек с которого осуществлялся перевод.'
        f'▪️ Возврат криптовалюты высоким риском производится в течении 24 часов отделом службы безопасности.'
        f'▪️ Обменный пункт в праве удержать комиссию до 5% при возврате денежных средств c высоким риском.'
        f'▪️ Обменный пункт может потребовать прохождение полной верификации клиента.'
        f'▪️ Перечень необходимых документов и материалов для верификации определяется индивидуально для каждого случая.\n'
        f'В этом случае Сервис Cripthub.ru оставляет за собой полное право:\n',
        f'1. Требовать от Клиента предоставить дополнительную информацию, раскрывающую происхождение цифровых '
        f'активов и/или подтверждение того, что эти активы не были получены преступным путем;',
        f'Заблокировать аккаунт и любые операции, связанные с Клиентом, передать в контролирующие финансовую '
        f'2. деятельность и/или правоохранительные органы по месту регистрации Сервиса и, при необходимости, по адресу '
        f'регистрации Клиента всю имеющуюся по инциденту информацию и документы;\n',
        f'3. Требовать от Клиента документы, подтверждающие личность, физическое существование, адрес регистрации, '
        f'платежеспособность;\n'
        f'4. Осуществлять возврат цифровых активов только на реквизиты, с которых перевод был осуществлен или перейти '
        f'на другие реквизиты, после полной проверки службой безопасности Сервиса, если удалось проверить '
        f'легальное происхождение средств Клиента;\n',
        f'5. Отказать Клиенту в выводе средств на счет третьих лиц без объяснения причин;\n',
        f'6. Удерживать средства Клиента до полного расследования инцидента;\n',
        f'7. Сервис оставляет за собой право контролировать всю цепочку транзакций, с целью выявления '
        f'подозрительных транзакций;\n',
        f'8. Сервис оставляет за собой право отказать Клиенту в предоставлении услуги, если у Сервиса есть '
        f'обоснованные подозрения в законности происхождения цифровых активов и удерживать средства '
        f'на специальных счетах Сервиса;\n',
        f'9. Сервис оставляет за собой право отказать Клиенту в предоставлении услуги, если у Сервиса есть '
        f'обоснованные подозрения в законности происхождения цифровых активов и удерживать средства на специальных '
        f'счетах Сервиса, в случае если невозможно отследить всю цепочку движения цифровых активов '
        f'с момента их появления.\n',
        f'Условия произведения возврата средств остановленных на проверку по итогам AML анализа транзакции:\n',
        f'Возврат средств осуществляется после полной проверки службой безопасности Сервиса, которая может включать '
        f'подробную верификацию отправителя. Возврат средств осуществляется за вычетом комиссии '
        f'до 5% от суммы транзакции на покрытие трудозатрат на обработку заявки и организацию возврата средств.',
        f'Возврат, при условии одобрения со стороны Сервиса, будет обработан Сервисом в течение 7 (семи) календарных '
        f'дней, начиная с даты, когда Пользователь был уведомлен с решением Сервиса относительно его '
        f'запроса на возврат.При оформлении возврата средств, после прохождения проверки(верификации), пользователь '
        f'обязан подтвердить реквизиты для получения возврата средств.'
    ]
    if isinstance(call, CallbackQuery):
        await call.message.edit_text(text='\n'.join(text), reply_markup=await back_to_manu_kb())
    elif isinstance(call, Message):
        await call.answer(text='\n'.join(text), reply_markup=await back_to_manu_kb())


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
