from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from retail_chain.models import ChainLink, Product
from retail_chain.serializers import ChainLinkSerializer, ProductSerializer


class RestoreMixin:
    """Общий механизм «мягкого» восстановления удалённого объекта."""

    model = None
    serializer_class = None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={"is_deleted": False}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RestoreChain(RestoreMixin, UpdateAPIView):
    """Восстановление удалённого элемента торговой цепи."""

    queryset = ChainLink.objects.all()
    serializer_class = ChainLinkSerializer


class RestoreProduct(RestoreMixin, UpdateAPIView):
    """Восстановление удалённого продукта."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
