from rest_framework.permissions import BasePermission


class ActiveUserPermission(BasePermission):
    """Допуск только активному пользователю."""

    message = "Только активный сотрудник имеет доступ."

    def has_permission(self, request, view):
        if not hasattr(request.user, "is_employer"):
            return False

        return request.user.is_authenticated and request.user.is_active
