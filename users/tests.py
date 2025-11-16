from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import CustomUser


class TestUsers(APITestCase):
    """ Тест модели пользователя. """

    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com", password="password", username="admin"
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_custom_user(self):
        """ Создание пользователя. """

        data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "phone_number": "+79876543210",
            "is_employer": True,
            "password": "password",
        }
        response = self.client.post(reverse("users:create_user"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = CustomUser.objects.get(email="newuser@example.com")
        self.assertIsNotNone(new_user)

    def test_update_custom_user(self):
        """ Обновление пользователя. """

        user_data = {"email": "update@example.com"}
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(reverse("users:update_user", kwargs={"pk": self.admin_user.pk}), data=user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = CustomUser.objects.get(pk=self.admin_user.pk)
        self.assertEqual(updated_user.email, "update@example.com")

    def test_retrieve_custom_user_detail(self):
        """ Детальная информация о пользователе. """

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse("users:info_user", kwargs={"pk": self.admin_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_delete_custom_user(self):
        """ Удаление пользователя. """

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(pk=self.admin_user.pk)
