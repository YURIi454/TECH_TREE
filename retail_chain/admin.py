from decimal import Decimal

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from retail_chain.models import ChainLink, Product


@admin.register(ChainLink)
class ChainLinkAdmin(admin.ModelAdmin):
    """Отображение модели звена торговой сети в админ панели."""

    list_display = (
        "name",
        "person",
        "supplier_link",
        "level",
        "email",
        "country",
        "city",
        "debt_to_supplier",
        "created_at",
        "is_deleted",
    )
    list_filter = (
        "country",
        "city",
        "is_deleted",
    )
    search_fields = ("name", "city", "email")
    readonly_fields = ("created_at", "updated_at", "supplier_link", "level")
    filter_horizontal = ("product",)
    actions = ("clear_debt_to_supplier",)

    @admin.display(description="Поставщик", ordering="supplier__name")
    def supplier_link(self, obj):
        """Ссылка на объект сети, являющийся поставщиком."""

        if obj.supplier_id is None:
            return "—"

        url = reverse("admin:retail_chain_chainlink_change", args=(obj.supplier_id,))
        return format_html('<a href="{}">{}</a>', url, obj.supplier)

    @admin.display(description="Уровень")
    def level(self, obj):
        """Номер уровня иерархии: завод — 0, розничная сеть — 1, ИП — 2."""

        return obj.level

    @admin.action(description="Очистить задолженность перед поставщиком")
    def clear_debt_to_supplier(self, request, queryset):
        """Снимает задолженность. Звенья без поставщика (заводы) не затрагиваются."""

        count = queryset.exclude(supplier__isnull=True).update(debt_to_supplier=Decimal("0.00"))
        self.message_user(request, f"Задолженность снята у {count} звеньев(ев) сети.")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Отображение продукта в админ панели."""

    list_display = (
        "name",
        "model",
        "release_date",
        "price",
        "created_at",
        "is_deleted",
    )
    list_filter = ("is_deleted",)
    search_fields = ("name", "model")
    readonly_fields = ("created_at", "updated_at")
