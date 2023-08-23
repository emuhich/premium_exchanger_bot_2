import asyncio
from datetime import datetime

from aiogram import Bot
from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from admin_panel.telebot.models import Mailing, Client
from tgbot.config import load_config
from tgbot.misc.mailing import send_message_mailing


@login_required
def mailing(request):
    template = 'tgbot/mailing.html'
    context = {}

    if request.method == 'POST':
        error = validate_mailing_form(request.POST)

        if error:
            context = {
                'message_text': request.POST.get('message_text'),
                'file_id': request.POST.get('file_id'),
                'schedule_datetime': request.POST.get('schedule_datetime'),
                'schedule_checkbox': 'schedule_checkbox' in request.POST,
                'error': error
            }
            return render(request, template, context)

        if 'schedule_checkbox' not in request.POST:
            count_send = run_mailing(
                request.POST.get('media_type'),
                request.POST.get('message_text'),
                request.POST.get('file_id'))

            context.update({
                'start_mailing': True,
                'count_send': count_send
            })
            return render(request, template, context)

        schedule_datetime = datetime.strptime(request.POST.get('schedule_datetime'), "%Y-%m-%dT%H:%M")
        mailing_obj = Mailing.objects.create(
            media_type=request.POST['media_type'],
            text=request.POST['message_text'],
            date_malling=schedule_datetime,
            file_id=request.POST['file_id']
        )
        url_name = f'admin:{mailing_obj._meta.app_label}_{mailing_obj._meta.model_name}_change'
        url = reverse(url_name, args=[mailing_obj.pk])
        context.update({
            'saved': True,
            'url': url
        })

    return render(request, template, context)


def validate_mailing_form(post_data):
    error = None
    media_type = post_data.get('media_type')
    message_text = post_data.get('message_text')
    fileid = post_data.get('file_id')
    schedule_checkbox = 'schedule_checkbox' in post_data
    schedule_datetime = post_data.get('schedule_datetime')

    if not media_type:
        error = "Не выбран тип медиа"
    elif media_type != "no_media" and not fileid:
        error = "Не указан File ID для медиа"
    elif media_type == "no_media" and not message_text:
        error = "Не указан текст рассылки"
    elif schedule_checkbox and not schedule_datetime:
        error = "Не указано время рассылки"
    elif media_type == "no_media" and len(message_text) > 4096:
        error = "Длина текста рассылки не должна превышать 4096 символов"
    elif media_type != "no_media" and len(message_text) > 1024:
        error = "Длина текста рассылки с медиа не должна превышать 1024 символа"

    return error


def run_mailing(media_type, message_text, file_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    count_send = loop.run_until_complete(mailing_django(media_type, message_text, file_id))
    return count_send


async def mailing_django(media, text, file_id):
    users = await sync_to_async(Client.objects.all)()
    config = load_config(".env")
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

    count_send = 0
    async for user in users:
        args = [user.telegram_id]
        kwargs = {}
        if media in ['photo', 'video', 'document']:
            args.append(file_id)
            kwargs["caption"] = text
        else:
            args.append(text)
        status = await send_message_mailing(bot, media, args, kwargs)
        if status:
            count_send += 1
    return count_send

