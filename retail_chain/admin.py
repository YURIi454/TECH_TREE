from django.contrib import admin

from retail_chain.models import ChainLink, Product


@admin.register(ChainLink)
class ChainAdmin(admin.ModelAdmin):
    """Отображение модели звена торговой сети в админ панели."""

    list_display = (
        "name",
        "person",
        "level",
        "email",
        "country",
        "city",
        "where_my_money",
        "created_at",
        "is_deleted",
    )

    list_filter = (
        "city",
        "is_deleted",
    )
    search_fields = ("city",)
    readonly_fields = ["created_at", "updated_at"]

    def debt_closed(self, request, queryset):
        """Снятие задолженности."""

        count = queryset.update(where_my_money=0)
        self.message_user(request, f"Сняли задолженность у {count} участников.")

    debt_closed.short_description = "Задолженность снята!"
    actions = [debt_closed]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Отображение продукта в админ панели."""

    list_display = [
        "name",
        "description",
        "price",
        "created_at",
        "is_deleted",
    ]

    search_fields = ("name",)
    readonly_fields = ["created_at", "updated_at"]
