import datetime

from django.db import migrations, models
from django.db.models import Q

UNKNOWN_COUNTRY = "Не указана"
UNKNOWN_CITY = "Не указан"


def _is_empty(field):
    return Q(**{f"{field}__isnull": True}) | Q(**{field: ""})


def fill_missing_contacts(apps, schema_editor):
    """Заполняет обязательные контакты, которые раньше могли быть пустыми."""

    ChainLink = apps.get_model("retail_chain", "ChainLink")
    db_alias = schema_editor.connection.alias

    ChainLink.objects.using(db_alias).filter(_is_empty("country")).update(country=UNKNOWN_COUNTRY)
    ChainLink.objects.using(db_alias).filter(_is_empty("city")).update(city=UNKNOWN_CITY)
    ChainLink.objects.using(db_alias).filter(_is_empty("street")).update(street="")

    # FK-ограничения объявлены DEFERRABLE INITIALLY DEFERRED, поэтому после UPDATE
    # остаются отложенные события триггеров, из-за которых PostgreSQL отклоняет
    # последующий ALTER TABLE (PGCODE 55006). Принудительно применяем их.
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")


def noop(apps, schema_editor):
    """Обратный переход для data-миграции (no-op)."""


class Migration(migrations.Migration):

    dependencies = [
        ("retail_chain", "0002_initial"),
    ]

    operations = [
        # --- Переименование «уровень» -> «поставщик» и уточнение названий полей ---
        migrations.RenameField(
            model_name="chainlink",
            old_name="level",
            new_name="supplier",
        ),
        migrations.RenameField(
            model_name="chainlink",
            old_name="where_my_money",
            new_name="debt_to_supplier",
        ),
        migrations.AlterField(
            model_name="chainlink",
            name="supplier",
            field=models.ForeignKey(
                blank=True,
                help_text="Звено сети, которое поставляет оборудование. Пусто — звено находится на уровне 0 (завод).",
                null=True,
                on_delete=models.SET_NULL,
                related_name="children",
                to="retail_chain.chainlink",
                verbose_name="поставщик",
            ),
        ),
        migrations.AlterField(
            model_name="chainlink",
            name="debt_to_supplier",
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                max_digits=12,
                verbose_name="задолженность перед поставщиком",
            ),
        ),
        # --- Продукт: обязательные «модель» и «дата выхода продукта на рынок» ---
        migrations.AddField(
            model_name="product",
            name="model",
            field=models.CharField(default="", max_length=150, verbose_name="модель"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="release_date",
            field=models.DateField(
                default=datetime.date(1970, 1, 1),
                verbose_name="дата выхода продукта на рынок",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0.00, max_digits=10, verbose_name="цена"),
        ),
        # --- Контакты звена сети становятся обязательными ---
        migrations.RunPython(fill_missing_contacts, noop),
        migrations.AlterField(
            model_name="chainlink",
            name="country",
            field=models.CharField(max_length=150, verbose_name="страна"),
        ),
        migrations.AlterField(
            model_name="chainlink",
            name="city",
            field=models.CharField(max_length=150, verbose_name="город"),
        ),
        migrations.AlterField(
            model_name="chainlink",
            name="street",
            field=models.CharField(blank=True, default="", max_length=200, verbose_name="улица"),
        ),
    ]
