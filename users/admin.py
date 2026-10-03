from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class UsersAdmin(admin.ModelAdmin):
    """Настройки отображения в админ панели."""

    list_display = ("id", "full_name", "email", "phone_number", "is_employer", "is_active", "is_deleted", "created_at")
    list_filter = ("is_employer", "is_active", "is_staff", "is_deleted")
    list_editable = ("is_employer", "is_active")
    search_fields = ("email", "full_name")
    readonly_fields = ("created_at", "updated_at", "last_login")
    actions = ("restore_users",)

    @admin.action(description="Восстановить выбранных пользователей")
    def restore_users(self, request, queryset):
        # is_active не восстанавливаем: аккаунт мог быть отключён отдельно.
        count = queryset.filter(is_deleted=True).update(is_deleted=False)
        self.message_user(request, f"Восстановлено пользователей: {count}.")
