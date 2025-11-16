from django.core.management.base import BaseCommand
from users.models import CustomUser
from retail_chain.models import Product, ChainLink


class Command(BaseCommand):
    """Заполняем базу тестовыми данными."""

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username="admin").exists():
            user = CustomUser.objects.create_superuser(
                username="admin",
                email="admin@admin.com",
                password="password",
                full_name="Администратор",
                is_employer=True,
            )
            self.stdout.write(f"Создан пользователь {user}")

            products = []

            for i in range(1, 3):
                product = Product.objects.create(name=f"Товар_{i}", price=i * 100)
                products.append(product)
                self.stdout.write(f'Создан продукт "{product}"')

            chain_links = []
            first_link = ChainLink.objects.create(name="Первый участник", person=user, house_number="1А")
            second_link = ChainLink.objects.create(
                name="Второй участник", person=user, level=first_link, house_number="2Б"
            )
            third_link = ChainLink.objects.create(
                name="Третий участник", person=user, level=second_link, house_number="3В"
            )
            chain_links.extend([first_link, second_link, third_link])

            for link in chain_links:
                link.product.set(products)
                self.stdout.write(f'Присвоены товары участнику "{link}"')

            self.stdout.write("Заполнение БД успешно завершилось!")

        self.stdout.write("Команда уже применялась, повторный запуск приведет к ошибкам!")
