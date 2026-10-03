from rest_framework.permissions import BasePermission


class ActiveUserPermission(BasePermission):
    """Доступ к API только для активных сотрудников.

    Сотрудником считается пользователь с is_employer=True.
    Неактивные сотрудники (is_active=False) и мягко удалённые
    (is_deleted=True) доступа не имеют.
    """

    message = "Доступ к API разрешён только активным сотрудникам."

    def has_permission(self, request, view):
        user = request.user

        if user is None or not user.is_authenticated:
            return False

        if not user.is_active:
            return False

        # Мягко удалённый сотрудник не имеет доступа ни к одной ручке,
        # кроме собственного восстановления

        if getattr(user, "is_deleted", False) and not getattr(view, "allow_deleted_user", False):
            return False

        return bool(getattr(user, "is_employer", False))
