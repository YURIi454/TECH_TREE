from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from retail_chain.models import ChainLink, Product
from users.models import CustomUser

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "password"

PRODUCTS = [
    ("Смартфон Galaxy", "SM-G920", date(2023, 3, 15), Decimal("64990.00")),
    ("Ноутбук ProBook", "PB-450", date(2022, 9, 1), Decimal("54990.00")),
    ("Телевизор OLED", "TV-O55", date(2024, 5, 20), Decimal("119990.00")),
    ("Планшет Tab", "TB-11", date(2023, 11, 3), Decimal("32990.00")),
]

CHAIN_LINKS = [
    ("Завод «Кристалл»", None, "Россия", "Москва", "ул. Заводская", "1", Decimal("0.00")),
    ("Розничная сеть «ТехноЛиния»", "Завод «Кристалл»", "Россия", "Москва", "ул. Тверская", "12",
     Decimal("150000.50")),
    ("Розничная сеть «Дом Электроники»", "Завод «Кристалл»", "Россия", "Санкт-Петербург", "Невский пр.",
     "45", Decimal("84500.00")),
    ("ИП Смирнов", "Розничная сеть «ТехноЛиния»", "Россия", "Казань", "ул. Баумана", "7",
     Decimal("12000.75")),
    ("ИП Кузнецова", "Розничная сеть «Дом Электроники»", "Беларусь", "Минск", "пр. Независимости", "30",
     Decimal("3300.10")),
]


class Command(BaseCommand):
    """Заполняет базу тестовыми данными."""

    help = "Наполняет БД данными ."

    def handle(self, *args, **options):
        user = CustomUser.objects.filter(username=ADMIN_USERNAME).first()
        if user is None:
            user = CustomUser.objects.create_superuser(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
                full_name="Администратор",
                is_employer=True,
            )
            self.stdout.write(f"Создан пользователь {user}")
        else:
            self.stdout.write(f"Пользователь {user} уже существует")

        products = {}
        for name, model, release_date, price in PRODUCTS:
            product, _ = Product.objects.update_or_create(
                name=name,
                defaults={"model": model, "release_date": release_date, "price": price},
            )
            products[name] = product
            self.stdout.write(f'Создан продукт "{product}"')

        links = {}
        for name, supplier_name, country, city, street, house, debt in CHAIN_LINKS:
            link, _ = ChainLink.objects.update_or_create(
                name=name,
                defaults={
                    "person": user,
                    "supplier": links.get(supplier_name),
                    "country": country,
                    "city": city,
                    "street": street,
                    "house_number": house,
                    "debt_to_supplier": debt,
                },
            )
            links[name] = link
            link.product.set(products.values())
            self.stdout.write(f'Создано звено сети "{link}" (уровень {link.level})')

        self.stdout.write("Заполнение БД успешно!")
