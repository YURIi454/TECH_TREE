from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Пользователь."""

    full_name = models.CharField(max_length=150, verbose_name="полное имя")
    email = models.EmailField(unique=True, verbose_name="Ваш Email")
    phone_number = models.CharField(null=True, blank=True, verbose_name="Телефон")
    is_employer = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменён")
    is_deleted = models.BooleanField(default=False, verbose_name='"на удаление"')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]
        db_table = "custom_user"
