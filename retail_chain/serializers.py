from rest_framework import serializers

from retail_chain.models import SUPPLIER_CYCLE_ERROR, SUPPLIER_SELF_ERROR, ChainLink, Product


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор продукта."""

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "model",
            "release_date",
            "description",
            "preview",
            "price",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ChainLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для звена торговой цепи."""

    product = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        source="product",
        many=True,
        queryset=Product.objects.filter(is_deleted=False),
        required=False,
        write_only=True,
        help_text="Список id продуктов, которые продаёт звено сети.",
    )
    level = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChainLink
        fields = [
            "id",
            "name",
            "person",
            "supplier",
            "level",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "product",
            "product_ids",
            "debt_to_supplier",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
        # Задолженность перед поставщителем нельзя изменить через API:
        # её обнуляет только admin action в админ-панели.
        read_only_fields = ["debt_to_supplier", "created_at", "updated_at", "level"]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if "supplier" not in attrs:
            return attrs

        supplier = attrs["supplier"]
        instance_pk = self.instance.pk if self.instance is not None else None

        if instance_pk is not None and supplier.pk == instance_pk:
            raise serializers.ValidationError({"supplier": SUPPLIER_SELF_ERROR})

        if ChainLink.has_supplier_cycle(supplier, instance_pk):
            raise serializers.ValidationError({"supplier": SUPPLIER_CYCLE_ERROR})

        return attrs


# Историческое имя сериализатора, чтобы не ломать существующие импорты.
ChainSerializer = ChainLinkSerializer
