from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView

from retail_chain.models import ChainLink, Product
from retail_chain.serializers import ChainSerializer, ProductSerializer
from users.permissions import ActiveUserPermission

from .services import RestoreChain, RestoreProduct  # noqa: F401


class CreateProduct(CreateAPIView):
    """Создание продукта."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return Product.objects.all()


class UpdateProduct(UpdateAPIView):
    """Редактирование продукта."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return Product.objects.filter(is_deleted=False)


class InfoProduct(RetrieveAPIView):
    """Подробная информация продукта."""

    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]

    def get_object(self):
        pk = self.kwargs["pk"]
        obj = Product.objects.get(pk=pk, is_deleted=False)
        return obj


class ListProduct(ListAPIView):
    """Список продуктов."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "is_deleted",
        "name",
    ]

    def get_queryset(self):
        queryset = Product.objects.filter(is_deleted=False)
        return queryset


class DeleteProduct(DestroyAPIView):
    """Удаление продукта."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]

    def perform_destroy(self, instance):
        """Установка статуса "на удаление"."""

        instance.is_deleted = True
        instance.save()

    def get_queryset(self):
        return Product.objects.all()


class CreateChain(CreateAPIView):
    """Создание элемента торговой цепи."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ChainSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return ChainLink.objects.all()


class UpdateChain(UpdateAPIView):
    """Редактирование элемента торговой цепи."""

    serializer_class = ChainSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return ChainLink.objects.all().filter(is_deleted=False)


class InfoChain(RetrieveAPIView):
    """Подробная информация элемента торговой цепи."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ChainSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        queryset = (
            ChainLink.objects.select_related("person")
            .select_related("level")
            .prefetch_related("product")
            .filter(is_deleted=False)
        )
        return queryset


class ListChain(ListAPIView):
    """Список элементов торговой цепи."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ChainSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_deleted", "name"]

    def get_queryset(self):
        queryset = (
            ChainLink.objects.select_related("person")
            .select_related("level")
            .prefetch_related("product")
            .filter(is_deleted=False)
        )
        return queryset


class DeleteChain(DestroyAPIView):
    """Удаление элемента торговой цепи."""

    permission_classes = [ActiveUserPermission]
    serializer_class = ChainSerializer
    filter_backends = [DjangoFilterBackend]

    def perform_destroy(self, instance):
        """Установка статуса "на удаление"."""

        instance.is_deleted = True
        instance.save()

    def get_queryset(self):
        return ChainLink.objects.all()
