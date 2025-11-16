from django.db import models
from django.db.models import SET_NULL

from config.settings import AUTH_USER_MODEL


class Product(models.Model):
    """Продукт."""

    name = models.CharField(unique=True, verbose_name="название продукта")
    description = models.TextField(blank=True, null=True, verbose_name="описание продукта")
    preview = models.URLField(blank=True, null=True, verbose_name="просмотр продукта")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="цена")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменён")

    is_deleted = models.BooleanField(default=False, verbose_name='"на удаление"')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]
        db_table = "product"


class ChainLink(models.Model):
    """Звено торговой сети."""

    name = models.CharField(unique=True, max_length=150)
    person = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=SET_NULL, blank=True, null=True, verbose_name="представитель"
    )
    level = models.ForeignKey(
        "self", blank=True, null=True, on_delete=SET_NULL, related_name="levels", verbose_name="уровень участника"
    )

    email = models.EmailField(blank=True, null=True, verbose_name="email")
    country = models.CharField(max_length=150, blank=True, null=True, verbose_name="страна")
    city = models.CharField(max_length=150, blank=True, null=True, verbose_name="город")
    street = models.CharField(max_length=200, blank=True, null=True, verbose_name="улица")
    house_number = models.CharField(max_length=10, verbose_name="номер дома")

    product = models.ManyToManyField("Product", blank=True, verbose_name="продукт")
    where_my_money = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="задолженность")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменён")

    is_deleted = models.BooleanField(default=False, verbose_name='"на удаление"')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участник"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["city"], name="chain_link_city_index"),
        ]
        db_table = "chain_link"
