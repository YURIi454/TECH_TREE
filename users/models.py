from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Менеджер пользователей.

    В проекте логином является email (USERNAME_FIELD = "email"), а поле username
    осталось от AbstractUser. Чтобы они не расходились, username выводится из
    email автоматически, если его не передали явно.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Пользователь должен иметь email.")

        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Суперпользователь админки по умолчанию считается сотрудником,
        # иначе он не сможет пользоваться API.

        extra_fields.setdefault("is_employer", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Пользователь."""

    full_name = models.CharField(max_length=150, verbose_name="полное имя")
    email = models.EmailField(unique=True, verbose_name="Ваш Email")
    phone_number = models.CharField(null=True, blank=True, verbose_name="Телефон")
    is_employer = models.BooleanField(default=False, verbose_name="сотрудник")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменён")
    is_deleted = models.BooleanField(default=False, verbose_name='"на удаление"')

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    # username выводится из email в менеджере, спрашивать его не нужно.
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]
        db_table = "custom_user"
