from django.contrib import admin
from django.contrib.admin import AdminSite, ModelAdmin

from admin_panel.telebot.models import Direction


class BotAdminSite(AdminSite):
    site_title = "Управление ботом"
    site_header = "Управление ботом"
    index_title = ""


bot_admin = BotAdminSite()


@admin.register(Direction, site=bot_admin)
class DirectionAdmin(ModelAdmin):
    list_display = (
        'direction_id',
        'name',
        'is_active',
        'pay_link',
        'info',
        'requisites',
        'direction_number',
    )
    list_display_links = ('direction_id',)
    empty_value_display = '-пусто-'
    list_editable = ('is_active', 'pay_link', 'info', 'requisites', 'direction_number')
    search_fields = ('direction_id', 'name',)
    list_filter = ('is_active', 'pay_link', 'info', 'requisites')
    list_per_page = 700

    class Meta:
        verbose_name_plural = 'Направления'
