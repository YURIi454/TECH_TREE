from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class UsersAdmin(admin.ModelAdmin):
    """ Настройки отображения в админ панели. """

    list_display = ("id", "full_name", "email", "phone_number", "created_at")
    list_filter = ("email",)
    search_fields = ("email",)
