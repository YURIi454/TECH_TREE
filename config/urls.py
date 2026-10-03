from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="admin:index", permanent=False), name="root"),
    path("retail_chain/", include("retail_chain.urls", "retail_chain")),
    path("users/", include("users.urls", "users")),
    path("api-auth/", include("rest_framework.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Админка подключается последней: admin.site.urls содержит catch-all
    # (r"^(.*)/$"), который перехватывает любой путь, не совпавший раньше.
    path("admin/", admin.site.urls),
]
