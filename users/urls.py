from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import CreateCustomUser, CustomUserDetail, DeleteCustomUser, UpdateCustomUser

app_name = "users"
router = DefaultRouter()
urlpatterns = [
    path("create_user/", CreateCustomUser.as_view(), name="create_user"),
    path("update_user/<int:pk>/", UpdateCustomUser.as_view(), name="update_user"),
    path("info_user/<int:pk>/", CustomUserDetail.as_view(), name="info_user"),
    path("delete_user/<int:pk>/", DeleteCustomUser.as_view(), name="delete_user"),
] + router.urls
