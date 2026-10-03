from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from retail_chain.admin import ChainLinkAdmin
from retail_chain.models import ChainLink, Product
from retail_chain.serializers import ChainLinkSerializer, ProductSerializer
from users.models import CustomUser


def make_user(email="admin@example.com", username="admin", is_employer=True, is_active=True):
    return CustomUser.objects.create_superuser(
        email=email,
        password="testpassword",
        username=username,
        full_name="Администратор",
        is_employer=is_employer,
        is_active=is_active,
    )


class TestRetailChain(APITestCase):
    """Тесты для моделей и представлений Retail Chain."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = make_user()
        self.client.force_authenticate(user=self.admin_user)

        self.product = Product.objects.create(
            name="Test Product",
            model="TP-1",
            release_date=date(2024, 1, 15),
            price=Decimal("100.00"),
        )
        self.factory = ChainLink.objects.create(
            name="Завод",
            country="Россия",
            city="Москва",
            street="ул. Заводская",
            house_number="1",
        )
        self.chain_link = ChainLink.objects.create(
            name="Розничная сеть",
            supplier=self.factory,
            country="Россия",
            city="Казань",
            street="ул. Баумана",
            house_number="2Б",
            debt_to_supplier=Decimal("500.25"),
        )

    def test_create_product(self):
        """Создание продукта."""

        data = {"name": "New Product", "model": "NP-2", "release_date": "2024-06-01", "price": "150.00"}

        response = self.client.post(reverse("retail_chain:product_create"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(Product.objects.filter(name="New Product").first())

    def test_create_product_requires_model_and_release_date(self):
        """Модель и дата выхода на рынок обязательны."""

        response = self.client.post(
            reverse("retail_chain:product_create"),
            data={"name": "Incomplete", "price": "10.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("model", response.data)
        self.assertIn("release_date", response.data)

    def test_update_product(self):
        """Редактирование продукта."""

        response = self.client.patch(
            reverse("retail_chain:product_update", kwargs={"pk": self.product.pk}),
            data={"name": "Updated Product Name"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product Name")

    def test_retrieve_product_detail(self):
        """Детальная информация о продукте."""

        response = self.client.get(reverse("retail_chain:product_info", kwargs={"pk": self.product.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ProductSerializer(instance=self.product).data)

    def test_retrieve_missing_product_returns_404(self):
        """Несуществующий продукт возвращает 404, а не 500."""

        response = self.client.get(reverse("retail_chain:product_info", kwargs={"pk": 999999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_products(self):
        """Получение списка продуктов."""

        response = self.client.get(reverse("retail_chain:product_list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = Product.objects.filter(is_deleted=False)
        self.assertEqual(response.data["results"], ProductSerializer(products, many=True).data)

    def test_delete_product(self):
        """Удаление продукта (soft delete)."""

        response = self.client.delete(reverse("retail_chain:product_delete", kwargs={"pk": self.product.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_deleted)

    def test_create_chain_link(self):
        """Создание звена торговой цепи."""

        data = {
            "name": "ИП Смирнов",
            "person": self.admin_user.pk,
            "supplier": self.chain_link.pk,
            "email": "ip@example.com",
            "country": "Россия",
            "city": "Омск",
            "street": "ул. Ленина",
            "house_number": "4321",
            "product_ids": [self.product.pk],
        }

        response = self.client.post(reverse("retail_chain:chain_create"), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = ChainLink.objects.get(name="ИП Смирнов")
        self.assertEqual(list(created.product.values_list("pk", flat=True)), [self.product.pk])
        self.assertEqual(created.level, 2)

    def test_create_chain_link_saves_contacts(self):
        """Контакты звена сохраняются через API."""

        data = {
            "name": "Контакты",
            "country": "Беларусь",
            "city": "Минск",
            "street": "пр. Независимости",
            "house_number": "30",
            "email": "contacts@example.com",
        }

        response = self.client.post(reverse("retail_chain:chain_create"), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = ChainLink.objects.get(name="Контакты")
        self.assertEqual(created.country, "Беларусь")
        self.assertEqual(created.city, "Минск")
        self.assertEqual(created.street, "пр. Независимости")
        self.assertEqual(created.house_number, "30")

    def test_update_chain_link(self):
        """Редактирование звена торговой цепи."""

        response = self.client.patch(
            reverse("retail_chain:chain_update", kwargs={"pk": self.chain_link.pk}),
            data={"name": "Updated Chain Link Name"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.chain_link.refresh_from_db()
        self.assertEqual(self.chain_link.name, "Updated Chain Link Name")

    def test_debt_to_supplier_is_read_only_via_api(self):
        """Задолженность перед поставщиком нельзя изменить через API."""

        response = self.client.patch(
            reverse("retail_chain:chain_update", kwargs={"pk": self.chain_link.pk}),
            data={"debt_to_supplier": "99999.99"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.chain_link.refresh_from_db()
        self.assertEqual(self.chain_link.debt_to_supplier, Decimal("500.25"))

    def test_debt_to_supplier_is_read_only_on_create(self):
        """Задолженность игнорируется и при создании звена через API."""

        response = self.client.post(
            reverse("retail_chain:chain_create"),
            data={
                "name": "С долгом",
                "country": "Россия",
                "city": "Москва",
                "house_number": "5",
                "debt_to_supplier": "777.77",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChainLink.objects.get(name="С долгом").debt_to_supplier, Decimal("0.00"))

    def test_retrieve_chain_link_detail(self):
        """Детальная информация о звене торговой цепи."""

        response = self.client.get(reverse("retail_chain:chain_info", kwargs={"pk": self.chain_link.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ChainLinkSerializer(instance=self.chain_link).data)
        self.assertEqual(response.data["level"], 1)

    def test_list_chain_links(self):
        """Получение списка звеньев торговой цепи."""

        response = self.client.get(reverse("retail_chain:chain_list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chain_links = ChainLink.objects.filter(is_deleted=False)
        self.assertEqual(response.data["results"], ChainLinkSerializer(chain_links, many=True).data)

    def test_delete_chain_link(self):
        """Удаление звена торговой цепи (soft delete)."""

        response = self.client.delete(reverse("retail_chain:chain_delete", kwargs={"pk": self.chain_link.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.chain_link.refresh_from_db()
        self.assertTrue(self.chain_link.is_deleted)

    def test_filter_chain_links_by_country(self):
        """Фильтрация объектов сети по стране."""

        belarus = ChainLink.objects.create(
            name="ИП Кузнецова", country="Беларусь", city="Минск", house_number="15"
        )

        response = self.client.get(reverse("retail_chain:chain_list"), data={"country": "Россия"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {item["name"] for item in response.data["results"]}
        self.assertEqual(names, {"Завод", "Розничная сеть"})
        self.assertNotIn(belarus.name, names)

    def test_filter_chain_links_by_country_is_case_insensitive(self):
        """Фильтр по стране нечувствителен к регистру."""

        response = self.client.get(reverse("retail_chain:chain_list"), data={"country": "россия"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_chain_links_by_unknown_country_returns_empty(self):
        """Фильтр по несуществующей стране возвращает пустой список."""

        response = self.client.get(reverse("retail_chain:chain_list"), data={"country": "Атлантида"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_filter_chain_links_by_city_and_ordering(self):
        """Фильтр по городу и сортировка через API."""

        response = self.client.get(
            reverse("retail_chain:chain_list"),
            data={"city": "Москва", "ordering": "-debt_to_supplier"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.data["results"]], ["Завод"])

    def test_level_is_derived_from_supplier(self):
        """Уровень определяется отношением к поставщику, а не названием."""

        ip = ChainLink.objects.create(
            name="ИП", supplier=self.chain_link, country="Россия", city="Омск", house_number="7"
        )

        self.assertEqual(self.factory.level, 0)
        self.assertEqual(self.chain_link.level, 1)
        self.assertEqual(ip.level, 2)

    def test_retail_network_directly_under_factory_has_level_1(self):
        """Розничная сеть, связанная напрямую с заводом, имеет уровень 1."""

        self.assertIsNone(self.factory.supplier)
        self.assertEqual(self.factory.level, 0)
        self.assertEqual(self.chain_link.supplier, self.factory)
        self.assertEqual(self.chain_link.level, 1)

    def test_supplier_cannot_be_the_link_itself(self):
        """Звено не может быть поставщиком самого себя."""

        response = self.client.patch(
            reverse("retail_chain:chain_update", kwargs={"pk": self.factory.pk}),
            data={"supplier": self.factory.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("supplier", response.data)

    def test_supplier_cycle_is_rejected(self):
        """Цикл в иерархии отклоняется."""

        ip = ChainLink.objects.create(
            name="ИП", supplier=self.chain_link, country="Россия", city="Омск", house_number="7"
        )

        # Завод -> ИП -> Розничная сеть -> Завод
        response = self.client.patch(
            reverse("retail_chain:chain_update", kwargs={"pk": self.factory.pk}),
            data={"supplier": ip.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.factory.refresh_from_db()
        self.assertIsNone(self.factory.supplier)

    def test_model_clean_detects_supplier_cycle(self):
        """Model.clean() также защищает от цикла (админка)."""

        self.factory.supplier = self.chain_link
        with self.assertRaises(Exception):
            self.factory.clean()

    def test_anonymous_has_no_access(self):
        """Анонимный пользователь не получает доступ к API."""

        response = APIClient().get(reverse("retail_chain:chain_list"))

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_inactive_employee_has_no_access(self):
        """Неактивный сотрудник не получает доступ к API."""

        self.admin_user.is_active = False
        self.admin_user.save()
        client = APIClient()
        client.force_authenticate(user=self.admin_user)

        response = client.get(reverse("retail_chain:chain_list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_non_employee_has_no_access(self):
        """Активный пользователь без признака сотрудника не получает доступ к API."""

        user = make_user(email="user@example.com", username="user", is_employer=False)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(reverse("retail_chain:chain_list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_api_also_requires_active_employee(self):
        """users-API не обходит проверку активного сотрудника."""

        self.admin_user.is_active = False
        self.admin_user.save()
        client = APIClient()
        client.force_authenticate(user=self.admin_user)

        response = client.get(reverse("users:info_user", kwargs={"pk": self.admin_user.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_does_not_shadow_api_urls(self):
        """Админка подключена на /admin/ и не перехватывает маршруты API."""

        self.assertEqual(reverse("admin:index"), "/admin/")
        response = self.client.get(reverse("retail_chain:chain_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_supplier_link(self):
        """В админке есть ссылка на поставщика."""

        model_admin = ChainLinkAdmin(ChainLink, None)

        self.assertEqual(model_admin.supplier_link(self.factory), "—")
        link_html = model_admin.supplier_link(self.chain_link)
        self.assertIn(f"/admin/retail_chain/chainlink/{self.factory.pk}/change/", link_html)
        self.assertIn("Завод", link_html)
        self.assertIn("supplier_link", model_admin.readonly_fields)

    def test_admin_clear_debt_action(self):
        """Admin action очищает задолженность только у звеньев с поставщиком."""

        admin_user = make_user(email="staff@example.com", username="staff")
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("admin:retail_chain_chainlink_changelist"),
            data={
                "action": "clear_debt_to_supplier",
                "_selected_action": [str(self.chain_link.pk)],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.chain_link.refresh_from_db()
        self.factory.refresh_from_db()
        self.assertEqual(self.chain_link.debt_to_supplier, Decimal("0.00"))

    def test_admin_city_filter_available(self):
        """В админке есть фильтр по городу и поиск."""

        model_admin = ChainLinkAdmin(ChainLink, None)

        self.assertIn("city", model_admin.list_filter)
        self.assertIn("city", model_admin.search_fields)
        self.assertIn("clear_debt_to_supplier", model_admin.actions)
