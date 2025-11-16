from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from retail_chain.models import ChainLink, Product
from retail_chain.serializers import ChainSerializer, ProductSerializer
from users.models import CustomUser


class TestRetailChain(APITestCase):
    """Тесты для моделей и представлений Retail Chain."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com", password="testpassword", username="admin", is_employer=True
        )
        self.client.force_authenticate(user=self.admin_user)

        self.product = Product.objects.create(name="Test Product", price=100.00)
        self.chain_link = ChainLink.objects.create(name="Test Link", where_my_money=50.00)

    def test_create_product(self):
        """Создание продукта."""

        data = {"name": "New Product", "price": 150.00}

        response = self.client.post(reverse("retail_chain:product_create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = Product.objects.get(name="New Product")
        self.assertIsNotNone(new_product)

    def test_update_product(self):
        """Обновление продукта."""

        data = {"name": "Updated Product Name"}

        response = self.client.patch(reverse("retail_chain:product_update", kwargs={"pk": self.product.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(updated_product.name, "Updated Product Name")

    def test_retrieve_product_detail(self):
        """Детальная информация продукта."""

        response = self.client.get(reverse("retail_chain:product_info", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_data = ProductSerializer(instance=self.product).data
        self.assertDictEqual(response.data, serialized_data)

    def test_list_products(self):
        """Получение списка продуктов."""

        response = self.client.get(reverse("retail_chain:product_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = Product.objects.filter(is_deleted=False)
        serialized_data = ProductSerializer(products, many=True).data
        self.assertListEqual(response.data["results"], serialized_data)

    def test_delete_product(self):
        """Удаление продукта."""

        response = self.client.delete(reverse("retail_chain:product_delete", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deleted_product = Product.objects.get(pk=self.product.pk)
        self.assertTrue(deleted_product.is_deleted)

    def test_create_chain_link(self):
        """Создание звена торговой цепи."""

        data = {
            "name": "New Chain Link",
            "person": self.admin_user.pk,
            "level": self.chain_link.pk,
            "email": "",
            "country": "",
            "city": "",
            "street": "",
            "house_number": "4321",
            "product": [
                self.product.pk,
            ],
            "where_my_money": 5412.21,
            "is_deleted": False,
        }

        response = self.client.post(reverse("retail_chain:chain_create"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_chain_link = ChainLink.objects.get(name="New Chain Link")
        self.assertIsNotNone(new_chain_link)

    def test_update_chain_link(self):
        """Обновление звена торговой цепи."""

        data = {"name": "Updated Chain Link Name"}
        response = self.client.patch(
            reverse("retail_chain:chain_update", kwargs={"pk": self.chain_link.pk}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_chain_link = ChainLink.objects.get(pk=self.chain_link.pk)
        self.assertEqual(updated_chain_link.name, "Updated Chain Link Name")

    def test_retrieve_chain_link_detail(self):
        """Детальная информация звена торговой цепи."""

        response = self.client.get(reverse("retail_chain:chain_info", kwargs={"pk": self.chain_link.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_data = ChainSerializer(instance=self.chain_link).data
        self.assertDictEqual(response.data, serialized_data)

    def test_list_chain_links(self):
        """Получение списка звеньев торговой цепи."""

        response = self.client.get(reverse("retail_chain:chain_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chain_links = ChainLink.objects.filter(is_deleted=False)
        serialized_data = ChainSerializer(chain_links, many=True).data
        self.assertListEqual(response.data["results"], serialized_data)

    def test_delete_chain_link(self):
        """Удаление звена торговой цепи."""

        response = self.client.delete(reverse("retail_chain:chain_delete", kwargs={"pk": self.chain_link.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deleted_chain_link = ChainLink.objects.get(pk=self.chain_link.pk)
        self.assertTrue(deleted_chain_link.is_deleted)
