import django_filters as filters

from retail_chain.models import ChainLink, Product


class ChainLinkFilter(filters.FilterSet):
    """Фильтры для списка звеньев торговой сети."""

    country = filters.CharFilter(field_name="country", lookup_expr="iexact", label="Страна")
    city = filters.CharFilter(field_name="city", lookup_expr="iexact", label="Город")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains", label="Название")
    supplier = filters.ModelChoiceFilter(field_name="supplier", queryset=ChainLink.objects.all())
    supplier__isnull = filters.BooleanFilter(field_name="supplier", lookup_expr="isnull")
    debt_to_supplier = filters.NumberFilter(field_name="debt_to_supplier")

    class Meta:
        model = ChainLink
        fields = ["is_deleted"]


class ProductFilter(filters.FilterSet):
    """Фильтры для списка продуктов."""

    name = filters.CharFilter(field_name="name", lookup_expr="icontains", label="Название")
    model = filters.CharFilter(field_name="model", lookup_expr="icontains", label="Модель")

    class Meta:
        model = Product
        fields = ["is_deleted"]
