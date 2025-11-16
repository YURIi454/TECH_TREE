from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from retail_chain.serializers import ChainSerializer, ProductSerializer
from users.permissions import ActiveUserPermission


class RestoreChain(UpdateAPIView, ActiveUserPermission):
    """Восстановление удалённого элемента торговой цепи."""

    serializer_class = ChainSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = {"is_deleted": False}
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RestoreProduct(UpdateAPIView, ActiveUserPermission):
    """Восстановление удалённого продукта."""

    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = {"is_deleted": False}
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
