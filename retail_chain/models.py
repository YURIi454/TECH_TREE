from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import SET_NULL

from config.settings import AUTH_USER_MODEL

SUPPLIER_SELF_ERROR = "Звено сети не может быть поставщиком самого себя."
SUPPLIER_CYCLE_ERROR = "Обнаружен цикл в иерархии сети: поставщик не может быть потомком звена."


class Product(models.Model):
    """Продукт."""

    name = models.CharField(unique=True, verbose_name="название продукта")
    model = models.CharField(max_length=150, verbose_name="модель")
    release_date = models.DateField(verbose_name="дата выхода продукта на рынок")
    description = models.TextField(blank=True, null=True, verbose_name="описание продукта")
    preview = models.URLField(blank=True, null=True, verbose_name="просмотр продукта")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="цена")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменён")

    is_deleted = models.BooleanField(default=False, verbose_name='"на удаление"')

    def __str__(self):
        return f"{self.name} ({self.model})"

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
    supplier = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name="children",
        verbose_name="поставщик",
        help_text="Звено сети, которое поставляет оборудование. Пусто — звено находится на уровне 0 (завод).",
    )

    email = models.EmailField(blank=True, null=True, verbose_name="email")
    country = models.CharField(max_length=150, verbose_name="страна")
    city = models.CharField(max_length=150, verbose_name="город")
    street = models.CharField(max_length=200, blank=True, default="", verbose_name="улица")
    house_number = models.CharField(max_length=10, verbose_name="номер дома")

    product = models.ManyToManyField("Product", blank=True, verbose_name="продукт")
    debt_to_supplier = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="задолженность перед поставщиком",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменён")

    is_deleted = models.BooleanField(default=False, verbose_name='"на удаление"')

    def __str__(self):
        return f"{self.name}"

    @property
    def level(self):
        """Номер уровня иерархии: завод — 0, розничная сеть — 1, ИП — 2."""

        level = 0
        supplier = self.supplier
        visited = {self.pk}
        while supplier is not None and supplier.pk not in visited:
            level += 1
            visited.add(supplier.pk)
            supplier = supplier.supplier
        return level

    @staticmethod
    def has_supplier_cycle(supplier, instance_pk=None):
        """Проверяет, что поставщик не создаёт цикл в иерархии.

        Цикл — это когда поставщик является потомком звена, которое мы сохраняем
        (в том числе когда это то же самое звено).
        """

        visited = {instance_pk} if instance_pk is not None else set()
        while supplier is not None:
            if supplier.pk in visited:
                return True
            visited.add(supplier.pk)
            supplier = supplier.supplier
        return False

    def clean(self):
        super().clean()

        if self.supplier_id is None:
            return

        if self.pk is not None and self.supplier_id == self.pk:
            raise ValidationError({"supplier": SUPPLIER_SELF_ERROR})

        if self.has_supplier_cycle(self.supplier, self.pk):
            raise ValidationError({"supplier": SUPPLIER_CYCLE_ERROR})

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["city"], name="chain_link_city_index"),
        ]
        db_table = "chain_link"
