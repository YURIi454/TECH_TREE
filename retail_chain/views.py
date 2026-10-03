from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView

from retail_chain.filters import ChainLinkFilter, ProductFilter
from retail_chain.models import ChainLink, Product
from retail_chain.serializers import ChainLinkSerializer, ProductSerializer


class CreateProduct(CreateAPIView):
    """Создание продукта."""

    serializer_class = ProductSerializer


class UpdateProduct(UpdateAPIView):
    """Редактирование продукта."""

    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_deleted=False)


class InfoProduct(RetrieveAPIView):
    """Подробная информация о продукте."""

    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_deleted=False)


class ListProduct(ListAPIView):
    """Список продуктов."""

    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering = ("name",)
    ordering_fields = ("name", "model", "price", "release_date", "created_at")

    def get_queryset(self):
        return Product.objects.filter(is_deleted=False)


class DeleteProduct(DestroyAPIView):
    """Удаление продукта (soft delete)."""

    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])


class CreateChain(CreateAPIView):
    """Создание элемента торговой цепи."""

    serializer_class = ChainLinkSerializer


class UpdateChain(UpdateAPIView):
    """Редактирование элемента торговой цепи."""

    serializer_class = ChainLinkSerializer

    def get_queryset(self):
        return ChainLink.objects.filter(is_deleted=False)


class InfoChain(RetrieveAPIView):
    """Подробная информация об элементе торговой цепи."""

    serializer_class = ChainLinkSerializer

    def get_queryset(self):
        return (
            ChainLink.objects.filter(is_deleted=False)
            .select_related("person", "supplier")
            .prefetch_related("product")
        )


class ListChain(ListAPIView):
    """Список элементов торговой цепи."""

    serializer_class = ChainLinkSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ChainLinkFilter
    ordering = ("name",)
    ordering_fields = ("name", "country", "city", "debt_to_supplier", "created_at")

    def get_queryset(self):
        return (
            ChainLink.objects.filter(is_deleted=False)
            .select_related("person", "supplier")
            .prefetch_related("product")
        )


class DeleteChain(DestroyAPIView):
    """Удаление элемента торговой цепи (soft delete)."""

    serializer_class = ChainLinkSerializer

    def get_queryset(self):
        return ChainLink.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])
