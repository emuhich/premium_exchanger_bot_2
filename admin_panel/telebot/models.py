from datetime import timedelta

from django.db import models
from django.utils import timezone


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения"
    )

    class Meta:
        abstract = True


class Client(CreatedModel):
    username = models.CharField(
        max_length=50,
        help_text='Username клиента',
        verbose_name='Username',
        blank=True,
        null=True
    )
    telegram_id = models.BigIntegerField(
        help_text='Telegram ID пользователя',
        verbose_name='Telegram ID'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Имя в Telegram',
        help_text='Имя в Telegram'
    )
    url = models.CharField(
        max_length=255,
        verbose_name='Ссылка на пользователя'
    )

    class Meta:
        verbose_name = 'Клиенты телеграмм бота'
        verbose_name_plural = 'Клиенты телеграмм бота'
        ordering = ('-created',)

    def __str__(self):
        return "{} ({})".format(self.username, self.telegram_id)


class SelectedDestinations(models.Model):
    user = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='selected',
        help_text='Пользователь который добавил в избранное',
        verbose_name='Пользователь'
    )
    name = models.CharField(
        help_text='Название избранного направления',
        verbose_name='Название',
        max_length=200
    )
    direction_id = models.CharField(
        help_text='ID избранного направления',
        verbose_name='ID',
        max_length=10
    )

    class Meta:
        verbose_name = 'Избранные направления'
        verbose_name_plural = 'Избранные направления'

    def __str__(self):
        return self.direction_id


class ExchangeHistory(CreatedModel):
    name = models.CharField(
        max_length=150,
        help_text='Направление сделки',
        verbose_name='Направление'
    )
    user = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='exchanges',
        help_text='Пользователь который совершил обмен',
        verbose_name='Пользователь'
    )
    exchange_id = models.IntegerField(
        help_text='ID обмена',
        verbose_name='ID'
    )
    status = models.CharField(
        verbose_name='Статус заявки',
        default='new',
        max_length=100
    )
    stop_check = models.DateTimeField(
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.stop_check = timezone.now() + timedelta(hours=2)
        super(CreatedModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'История обменов'
        verbose_name_plural = 'История обменов'
        ordering = ('-created',)

    def __str__(self):
        return str(self.exchange_id)
