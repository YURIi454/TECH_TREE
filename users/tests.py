from django.conf import settings
from django.contrib import admin
from django.test import Client, TestCase
from django.utils import translation
from django.utils.translation import gettext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.forms import StaffAuthenticationForm
from users.models import CustomUser


class TestUsers(APITestCase):
    """Тесты API пользователей."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="password",
            full_name="Администратор",
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_username_is_derived_from_email(self):
        """username выводится из email, отдельный логин не нужен."""

        user = CustomUser.objects.create_user(email="user@example.com", password="password123")

        self.assertEqual(user.username, "user@example.com")
        self.assertEqual(CustomUser.REQUIRED_FIELDS, [])

    def test_create_superuser_is_employee(self):
        """Суперпользователь, созданный createsuperuser, получает доступ к API."""

        self.assertTrue(self.admin_user.is_employer)
        self.assertTrue(self.admin_user.is_staff)

    def test_create_custom_user(self):
        """Создание пользователя."""

        data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "phone_number": "+79876543210",
            "is_employer": True,
            "password": "password123",
        }

        response = self.client.post(reverse("users:create_user"), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = CustomUser.objects.get(email="newuser@example.com")
        self.assertTrue(created.has_usable_password())
        self.assertTrue(created.check_password("password123"))
        self.assertEqual(created.username, "newuser@example.com")
        self.assertNotIn("password", response.data)

    def test_create_multiple_users_gets_unique_username(self):
        """Второй пользователь создаётся без ошибки уникальности username."""

        first = CustomUser.objects.create_user(email="first@example.com", password="password123")
        self.assertEqual(first.username, "first@example.com")

        response = self.client.post(
            reverse("users:create_user"),
            data={
                "email": "second@example.com",
                "full_name": "Second User",
                "password": "password123",
                "is_employer": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.get(email="second@example.com").username, "second@example.com")

    def test_cannot_grant_employee_status_to_self(self):
        """Пользователь не может выдать себе доступ к API через API."""

        response = self.client.patch(
            reverse("users:update_user", kwargs={"pk": self.admin_user.pk}),
            data={"is_employer": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_employer)

    def test_update_custom_user(self):
        """Редактирование пользователя."""

        response = self.client.patch(
            reverse("users:update_user", kwargs={"pk": self.admin_user.pk}),
            data={"full_name": "Новое имя"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.full_name, "Новое имя")

    def test_retrieve_custom_user_detail(self):
        """Детальная информация о пользователе."""

        response = self.client.get(reverse("users:info_user", kwargs={"pk": self.admin_user.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "admin@example.com")

    def test_cannot_read_other_users_data(self):
        """Пользователь видит только себя."""

        other = CustomUser.objects.create_user(email="other@example.com", password="password123")

        response = self.client.get(reverse("users:info_user", kwargs={"pk": other.pk}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_custom_user_is_soft(self):
        """Удаление пользователя помечает запись удалённой, а не стирает её."""

        response = self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_deleted)
        # is_active не трогается: иначе восстановить себя уже невозможно.
        self.assertTrue(self.admin_user.is_active)
        self.assertTrue(CustomUser.objects.filter(pk=self.admin_user.pk).exists())

    def test_deleted_user_loses_api_access(self):
        """Мягко удалённый сотрудник теряет доступ к API."""

        self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))
        self.client.force_authenticate(user=CustomUser.objects.get(pk=self.admin_user.pk))

        response = self.client.get(reverse("retail_chain:chain_list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleted_user_can_still_restore_itself(self):
        """Удалённый сотрудник может вернуть себе доступ через restore_user."""

        self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))
        self.client.force_authenticate(user=CustomUser.objects.get(pk=self.admin_user.pk))

        blocked = self.client.get(reverse("retail_chain:chain_list"))
        self.assertEqual(blocked.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse("users:restore_user", kwargs={"pk": self.admin_user.pk}),
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=CustomUser.objects.get(pk=self.admin_user.pk))
        self.assertEqual(self.client.get(reverse("retail_chain:chain_list")).status_code, status.HTTP_200_OK)

    def test_restore_custom_user(self):
        """Восстановление мягко удалённого пользователя."""

        self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))

        response = self.client.patch(
            reverse("users:restore_user", kwargs={"pk": self.admin_user.pk}),
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user.refresh_from_db()
        self.assertFalse(self.admin_user.is_deleted)
        self.assertTrue(self.admin_user.is_active)

    def test_deleted_user_is_hidden_from_own_profile(self):
        """Удалённый пользователь не видит свой профиль."""

        self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))
        # Перечитываем пользователя, как это делает JWT-аутентификация.
        self.client.force_authenticate(user=CustomUser.objects.get(pk=self.admin_user.pk))

        response = self.client.get(reverse("users:info_user", kwargs={"pk": self.admin_user.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleted_user_still_hidden_when_using_stale_object(self):
        """Даже с устаревшим объектом в памяти профиль удалённого скрыт."""

        self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))

        response = self.client.get(reverse("users:info_user", kwargs={"pk": self.admin_user.pk}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deleted_user_cannot_delete_again(self):
        """Повторный запрос удаления для удалённого пользователя даёт 404."""

        self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))

        response = self.client.delete(reverse("users:delete_user", kwargs={"pk": self.admin_user.pk}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_has_no_access(self):
        """Анонимный пользователь не получает доступ к API пользователей."""

        response = APIClient().get(reverse("users:info_user", kwargs={"pk": self.admin_user.pk}))

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


class TestAdminLoginByEmail(TestCase):
    """Вход в админку осуществляется по email, а не по отдельному username."""

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_superuser(
            email="boss@example.com",
            password="password",
            full_name="Директор",
        )

    def test_login_form_is_installed_on_admin_site(self):
        """Кастомная форма подключена через UsersConfig.ready()."""

        self.assertIs(admin.site.login_form, StaffAuthenticationForm)

    def test_login_field_is_labeled_email(self):
        """Поле ввода подписано «Email», а не «Username»."""

        with translation.override("en"):
            form = StaffAuthenticationForm()

            # Подпись переводится, поэтому сравниваем с переводом, а не со строкой.
            self.assertEqual(str(form.fields["username"].label), gettext("Email"))
            self.assertTrue(form.fields["username"].widget.attrs.get("autofocus"))

    def test_login_page_contains_email_label(self):
        """Страница входа показывает подпись «Email», а не «Username»."""

        with translation.override("en"):
            response = self.client.get("/admin/login/")

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, gettext("Email"))
            self.assertNotContains(response, gettext("Username"))

    def test_login_with_email_succeeds(self):
        """Вход по email и паролю."""

        response = self.client.post("/admin/login/", {"username": "boss@example.com", "password": "password"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("_auth_user_id"), str(self.user.pk))

    def test_login_uses_email_not_username(self):
        """Вход идёт по email, даже если username отличается от него."""

        self.user.username = "legacy-login"
        self.user.save(update_fields=["username"])

        by_username = self.client.post("/admin/login/", {"username": "legacy-login", "password": "password"})
        self.assertEqual(by_username.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

        by_email = self.client.post("/admin/login/", {"username": "boss@example.com", "password": "password"})
        self.assertEqual(by_email.status_code, 302)
        self.assertEqual(self.client.session.get("_auth_user_id"), str(self.user.pk))

    def test_invalid_credentials_show_email_hint(self):
        """Ошибка входа подсказывает, что нужен email, а не username."""

        response = self.client.post("/admin/login/", {"username": "boss@example.com", "password": "wrong"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Введите правильный email и пароль сотрудника")


class TestAllowedHosts(TestCase):
    """ALLOWED_HOSTS ограничивает перечень допустимых хостов."""

    def test_allowed_host_is_accepted(self):
        """Запрос с разрешённого хоста обрабатывается."""

        response = self.client.post("/api/token/", {"email": "nobody@example.com", "password": "wrong"})

        self.assertNotEqual(response.status_code, 400)

    def test_unknown_host_is_rejected(self):
        """Запрос с чужого Host-заголовка отклоняется."""

        response = self.client.post(
            "/api/token/",
            {"email": "nobody@example.com", "password": "wrong"},
            HTTP_HOST="evil.example.com",
        )

        self.assertEqual(response.status_code, 400)

    def test_wildcard_is_not_configured(self):
        """В настройках не осталось ALLOWED_HOSTS = '*'."""

        self.assertNotEqual(settings.ALLOWED_HOSTS, ["*"])
        self.assertFalse(settings.DEBUG)
