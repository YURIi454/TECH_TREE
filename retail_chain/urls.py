from django.urls import path

from retail_chain.services import RestoreChain, RestoreProduct
from retail_chain.views import (
    CreateChain,
    CreateProduct,
    DeleteChain,
    DeleteProduct,
    InfoChain,
    InfoProduct,
    ListChain,
    ListProduct,
    UpdateChain,
    UpdateProduct,
)

app_name = "retail_chain"

urlpatterns = [
    path("product_create/", CreateProduct.as_view(), name="product_create"),
    path("product_update/<int:pk>/", UpdateProduct.as_view(), name="product_update"),
    path("product_info/<int:pk>/", InfoProduct.as_view(), name="product_info"),
    path("product_list/", ListProduct.as_view(), name="product_list"),
    path("product_delete/<int:pk>/", DeleteProduct.as_view(), name="product_delete"),
    path("product_restore/<int:pk>/", RestoreProduct.as_view(), name="product_restore"),

    path("chain_create/", CreateChain.as_view(), name="chain_create"),
    path("chain_update/<int:pk>/", UpdateChain.as_view(), name="chain_update"),
    path("chain_info/<int:pk>/", InfoChain.as_view(), name="chain_info"),
    path("chain_list/", ListChain.as_view(), name="chain_list"),
    path("chain_delete/<int:pk>/", DeleteChain.as_view(), name="chain_delete"),
    path("chain_restore/<int:pk>/", RestoreChain.as_view(), name="chain_restore"),
]
