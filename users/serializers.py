from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для чтения и частичного обновления."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "is_employer",
            "is_active",
            "is_deleted",
            "created_at",
        ]
        # is_employer нельзя выдать себе через API — это право выдаёт администратор.
        read_only_fields = ["created_at", "is_employer", "is_active", "is_deleted"]


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "is_employer",
            "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password", "") or ""
        # username остаётся обязательным полем AbstractUser, но выводится
        # менеджером из email, поэтому отдельно его передавать не нужно.
        return CustomUser.objects.create_user(password=password, **validated_data)


class CustomUserRestoreSerializer(serializers.ModelSerializer):
    """Сериализатор восстановления мягко удалённого пользователя.

    is_active  отсутствует: состояние аккаунта меняет администратор,
    а мягкое удаление его не трогает.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "email", "is_deleted"]
        read_only_fields = ["id", "email"]
