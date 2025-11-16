from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, DestroyAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser
from users.serializers import CustomUserSerializer


class CreateCustomUser(CreateAPIView):
    """Создание пользователя."""

    serializer_class = CustomUserSerializer
    filter_backends = [DjangoFilterBackend]


class UpdateCustomUser(RetrieveUpdateAPIView):
    """Редактирование пользователя."""

    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    permission_classes = [IsAuthenticated, ]
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)


class CustomUserDetail(RetrieveAPIView):
    """ Просмотр данных пользователя. """

    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    permission_classes = [IsAuthenticated, ]
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)


class DeleteCustomUser(DestroyAPIView):
    """ Удаление пользователя. """

    serializer_class = CustomUserSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)
