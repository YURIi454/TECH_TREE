from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """Подменяем форму входа в админку на версию с понятной подписью «Email»."""

        from django.contrib import admin

        from .forms import StaffAuthenticationForm

        admin.site.login_form = StaffAuthenticationForm
