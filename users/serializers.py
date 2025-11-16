from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "created_at",
        ]
