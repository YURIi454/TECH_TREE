from rest_framework import serializers

from retail_chain.models import ChainLink, Product


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор продукта."""

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "created_at",
            "updated_at",
            "is_deleted",
        ]


class ChainSerializer(serializers.ModelSerializer):
    """Сериализатор для звена торговой цепи."""

    product = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ChainLink
        fields = [
            "name",
            "person",
            "level",
            "email",
            "city",
            "product",
            "where_my_money",
            "created_at",
            "is_deleted",
        ]
