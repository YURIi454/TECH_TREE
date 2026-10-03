from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response

from users.models import CustomUser
from users.serializers import (
    CustomUserCreateSerializer,
    CustomUserRestoreSerializer,
    CustomUserSerializer,
)


class OwnProfileMixin:
    """Доступ только к собственному профилю, без мягко удалённых записей."""

    def get_queryset(self) -> QuerySet:
        return CustomUser.objects.filter(id=self.request.user.id, is_deleted=False)


class CreateCustomUser(CreateAPIView):
    """Создание пользователя."""

    serializer_class = CustomUserCreateSerializer


class UpdateCustomUser(OwnProfileMixin, RetrieveUpdateAPIView):
    """Редактирование пользователя."""

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    serializer_class = CustomUserSerializer


class CustomUserDetail(OwnProfileMixin, RetrieveAPIView):
    """Просмотр данных пользователя."""

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    serializer_class = CustomUserSerializer


class DeleteCustomUser(OwnProfileMixin, DestroyAPIView):
    """Мягкое удаление пользователя.

    Запись остаётся в БД, но помечается удалённой. Доступ к API закрывается
    через ActiveUserPermission, а is_active не меняется
    """

    serializer_class = CustomUserSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])


class RestoreCustomUser(UpdateAPIView):
    """Восстановление мягко удалённого пользователя.
    Разрешаем доступ мягко удалённому пользователю только здесь.
    """

    serializer_class = CustomUserRestoreSerializer
    allow_deleted_user = True

    def get_queryset(self) -> QuerySet:
        return CustomUser.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={"is_deleted": False}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(CustomUserSerializer(instance).data, status=status.HTTP_200_OK)
