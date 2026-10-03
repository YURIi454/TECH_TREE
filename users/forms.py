from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _


class StaffAuthenticationForm(AdminAuthenticationForm):
    """Форма входа в админ-панель."""

    username = UsernameField(
        label=_("Email"),
        max_length=254,
        widget=AdminAuthenticationForm.base_fields["username"].widget,
        help_text=_("Введите email, который был указан при создании пользователя."),
    )
    error_messages = {
        **AdminAuthenticationForm.error_messages,
        "invalid_login": _(
            "Введите правильный email и пароль сотрудника. Учтите, что оба поля чувствительны к регистру."
        ),
    }
