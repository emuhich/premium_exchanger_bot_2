# Generated by Django 4.2 on 2023-08-11 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telebot', '0003_alter_exchangehistory_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangehistory',
            name='status',
            field=models.CharField(default='new', max_length=100, verbose_name='Статус заявки'),
        ),
        migrations.AddField(
            model_name='exchangehistory',
            name='stop_check',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]