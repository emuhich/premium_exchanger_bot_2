from datetime import datetime

import pytz
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone

from admin_panel.telebot.models import Client, SelectedDestinations, ExchangeHistory, Mailing, Direction


@sync_to_async()
def select_client(telegram_id):
    """
    Возвращает пользователя по телеграм ID
    """
    return Client.objects.filter(telegram_id=telegram_id).first()


@sync_to_async()
def create_client(username, telegram_id, url, name):
    """
    Создает пользователя
    """
    Client.objects.create(telegram_id=telegram_id, username=username, url=url, name=name)


@sync_to_async()
def create_super_user(username, password):
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, password=password)


@sync_to_async()
def create_selected_directions(user, direction_id, name):
    SelectedDestinations.objects.create(user=user, direction_id=direction_id, name=name)


@sync_to_async()
def create_exchange_db(user, name, exchange_id):
    return ExchangeHistory.objects.create(user=user, name=name, exchange_id=exchange_id)


@sync_to_async()
def get_exchange(exchange_id):
    return ExchangeHistory.objects.get(pk=exchange_id)


@sync_to_async()
def get_direction(direction_id):
    return SelectedDestinations.objects.get(pk=direction_id)


@sync_to_async()
def get_all_exchangers():
    return ExchangeHistory.objects.filter(stop_check__gte=timezone.now())


@sync_to_async()
def get_all_malling():
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    return Mailing.objects.filter(is_sent=False, date_malling__lte=now)


@sync_to_async()
def get_all_users():
    return Client.objects.all()


@sync_to_async()
def get_direction(direction_id):
    return Direction.objects.filter(direction_id=direction_id).first()


@sync_to_async()
def add_direction(direction_id, name):
    Direction.objects.create(direction_id=direction_id, name=name)


@sync_to_async()
def get_inactive_direction():
    return list(Direction.objects.filter(is_active=False).values_list('direction_id', flat=True))


@sync_to_async()
def sorted_direction_db():
    direction = Direction.objects.all()
    result = {}
    for i in direction:
        result.update({i.direction_id: i.direction_number if i.direction_number else 100})
    return result
