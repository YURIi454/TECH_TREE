# Проект TECH TREE

###### Technical Tree — торговая сеть электроники

## Описание проекта

Веб-приложение с REST API (DRF) и админ-панелью для управления иерархической
сетью продажи электроники.

######  в следующих версиях будет прикручен UI дождитесь релиза

**Модель сети** — `ChainLink` (звено сети):

* уровень 0 — завод;
* уровень 1 — розничная сеть, ссылающаяся напрямую на завод;
* уровень 2 — индивидуальный предприниматель.

Уровень **не хранится** в БД, а вычисляется как `ChainLink.level` по длине цепочки
поставщиков, поэтому переименование звена не ломает иерархию, а «минуя остальные
звенья» корректно даёт уровень 1. Циклы и ссылка на самого себя отклоняются
(`ChainLink.clean()` + валидация в сериализаторе).

**Продукты** — `Product`: название, модель, дата выхода на рынок, описание,
ссылка, цена.

## Реализованные требования

| Требование | Где реализовано |
|---|---|
| Иерархия из трёх уровней, поставщик — произвольное звено | `retail_chain/models.py` (`ChainLink.supplier`, `ChainLink.level`) |
| Контакты: email, страна, город, улица, дом | `ChainLink.email/country/city/street/house_number` |
| Продукты: название, модель, дата выхода на рынок | `Product.name/model/release_date` |
| Задолженность перед поставщиком (до копеек) | `ChainLink.debt_to_supplier` (`DecimalField(decimal_places=2)`) |
| Время создания (автоматически) | `ChainLink.created_at` (`auto_now_add=True`) |
| Вывод созданных объектов в админ-панели | `retail_chain/admin.py` (`list_display`) |
| Ссылка на «Поставщика» на странице объекта | `ChainLinkAdmin.supplier_link` |
| Фильтр по названию города в админке | `ChainLinkAdmin.list_filter` / `search_fields` |
| Admin action «очистить задолженность» | `ChainLinkAdmin.clear_debt_to_supplier` |
| CRUD для звена сети через DRF | `retail_chain/views.py`, `retail_chain/urls.py` |
| **Запрет обновления задолженности через API** | `ChainLinkSerializer.Meta.read_only_fields` |
| **Фильтрация по стране** | `retail_chain/filters.py` (`ChainLinkFilter.country`), `?country=Россия` |
| **Доступ только активным сотрудникам** | `users/permissions.py::ActiveUserPermission` |

Дополнительно: soft delete (`is_deleted`) с восстановлением для сетей, продуктов и
пользователей, фильтрация по городу, имени и поставщику, сортировка,
JWT-аутентификация, вход в админку по email, OpenAPI-схема (drf-spectacular),
настройки безопасности через `.env` (`ALLOWED_HOSTS`, `SECURE_SSL`, HSTS).

## Установка и настройка

### Python 3.12+ (Django 5.2 требует 3.10+)

```bash
python -m venv env

# Linux/macOS
source env/bin/activate
# Windows
env\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

Либо через Poetry:

```bash
poetry install
poetry shell
```

### Переменные окружения

Скопируйте `.env.sample` в `.env` и заполните значения:

```bash
cp .env.sample .env      # Linux/macOS
copy .env.sample .env    # Windows
```

| Переменная | Назначение |
|---|---|
| `SECRET_KEY` | секретный ключ Django (обязательно) |
| `NAME` | имя базы данных PostgreSQL |
| `USER` | пользователь БД |
| `PASSWORD` | пароль БД |
| `HOST` | хост БД (`localhost`) |
| `PORT` | порт БД (`5432`) |
| `DEBUG` | режим отладки |
| `ALLOWED_HOSTS` | список хостов через запятую (в продакшне обязательно) |
| `SECURE_SSL` | `True`, если приложение обслуживается по HTTPS |
| `SECURE_HSTS_SECONDS` | срок HSTS в секундах (по умолчанию год) |
| `USE_X_FORWARDED_PROTO` | `True`, если HTTPS терминируется на прокси |

Значения по умолчанию для локальной разработки — `DEBUG=False` и
`ALLOWED_HOSTS=localhost,127.0.0.1,[::1]`.

Все HTTPS-настройки (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`,
`CSRF_COOKIE_SECURE`, HSTS) выключаются одним флагом `SECURE_SSL`, чтобы
локальная разработка по http продолжала работать. Проверить готовность
к продакшну:

```bash
SECURE_SSL=True python manage.py check --deploy
```

### Запуск

```bash
python manage.py migrate
python manage.py runserver
```

Миграции уже сгенерированы и лежат в репозитории — `makemigrations` при
установке запускать не нужно.

* Админ-панель: <http://127.0.0.1:8000/admin/>
* Swagger UI: <http://127.0.0.1:8000/api/docs/swagger/>
* ReDoc: <http://127.0.0.1:8000/api/docs/redoc/>
* Схема OpenAPI: <http://127.0.0.1:8000/api/schema/>

### Демонстрационные данные

```bash
python manage.py add_all_data
```

Команда идемпотентна: создаёт суперпользователя `admin` / `admin@admin.com`
(пароль `password`), 4 продукта и 5 звеньев сети, расставленным по трём уровням.

### Вход по email

Логином служит **email**, а не отдельное имя пользователя. Поле `username`,
унаследованное от `AbstractUser`, автоматически заполняется значением email
(`users.models.CustomUserManager`), поэтому вводить его не нужно ни при
создании пользователя, ни в админ-панели — там поле подписано «Email»
(`users/forms.py::StaffAuthenticationForm`).

Поле `username` остаётся в модели, чтобы не терять совместимость с
`AbstractUser` и миграциями. Вход по старому значению `username` не работает.

## Доступ к API

Аутентификация — JWT (SimpleJWT) либо Token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -d "email=admin@admin.com&password=password"
```

Далее передаётся заголовок `Authorization: Bearer <access>`.

**Важно:** доступ к API получают только *активные сотрудники* — у пользователя
должны быть `is_active=True` **и** `is_employer=True`. Созданный через
`createsuperuser` пользователь сотрудником уже является: `CustomUserManager`
проставляет `is_employer=True`, поэтому доступ к API работает сразу.

Пользователь, созданный через `/users/create_user/`, сотрудником **не**
становится — этот флаг выдаёт администратор (в админке или через
`manage.py shell`).

## Примеры запросов

Получить JWT:

```http
POST /api/token/
Content-Type: application/x-www-form-urlencoded

email=admin@admin.com&password=password
```

Фильтрация по стране (регистр не важен):

```http
GET /retail_chain/chain_list/?country=Россия
Authorization: Bearer <access>
```

Фильтрация по городу, имени, поставщику, задолженности + сортировка:

```http
GET /retail_chain/chain_list/?city=Москва&debt_to_supplier__gt=0&ordering=-created_at
GET /retail_chain/chain_list/?supplier=1
GET /retail_chain/chain_list/?supplier__isnull=true      # только заводы
```

Создание звена сети (продукты задаются через `product_ids`):

```http
POST /retail_chain/chain_create/
{
  "name": "ИП Смирнов",
  "supplier": 2,
  "email": "ip@example.com",
  "country": "Россия",
  "city": "Омск",
  "street": "ул. Ленина",
  "house_number": "7",
  "product_ids": [1, 2]
}
```

Создание продукта:

```http
POST /retail_chain/product_create/
{
  "name": "Смартфон",
  "model": "SM-G920",
  "release_date": "2023-03-15",
  "price": "64990.00"
}
```

`debt_to_supplier` в ответах доступен только для чтения: попытка изменить его
через `POST`/`PATCH` игнорируется, задолженность снимается исключительно
admin action в админ-панели.

### Карта ручек

| Метод | Путь | Назначение |
|---|---|---|
| `GET` | `/retail_chain/chain_list/` | список звеньев (фильтры, сортировка, пагинация) |
| `POST` | `/retail_chain/chain_create/` | создать звено |
| `GET` | `/retail_chain/chain_info/<pk>/` | одно звено |
| `PUT`/`PATCH` | `/retail_chain/chain_update/<pk>/` | изменить звено |
| `DELETE` | `/retail_chain/chain_delete/<pk>/` | мягкое удаление звена |
| `PATCH` | `/retail_chain/chain_restore/<pk>/` | восстановить звено |
| `GET` | `/retail_chain/product_list/` | список продуктов |
| `POST` | `/retail_chain/product_create/` | создать продукт |
| `GET` | `/retail_chain/product_info/<pk>/` | один продукт |
| `PUT`/`PATCH` | `/retail_chain/product_update/<pk>/` | изменить продукт |
| `DELETE` | `/retail_chain/product_delete/<pk>/` | мягкое удаление продукта |
| `PATCH` | `/retail_chain/product_restore/<pk>/` | восстановить продукт |
| `POST` | `/users/create_user/` | создать пользователя |
| `GET` | `/users/info_user/<pk>/` | профиль (только свой) |
| `PUT`/`PATCH` | `/users/update_user/<pk>/` | изменить профиль (только свой) |
| `DELETE` | `/users/delete_user/<pk>/` | мягко удалить профиль (только свой) |
| `PATCH` | `/users/restore_user/<pk>/` | восстановить профиль (только свой) |

### Удаление и восстановление пользователя

`DELETE /users/delete_user/<pk>/` — мягкое удаление: запись остаётся в БД с
`is_deleted=True`. Доступ к API при этом теряется (`users/permissions.py`),
но `is_active` **не** меняется — иначе запрос на восстановление не прошёл бы
проверку прав.

Вернуть доступ:

```http
PATCH /users/restore_user/<pk>/
Authorization: Bearer <access>
```

Это единственный эндпоинт, доступный «удалённому» пользователю. В
админ-панели есть фильтр «на удаление» и action «Восстановить выбранных
пользователей»; `is_active` при этом не возвращается, аккаунт мог быть
отключён отдельно.

## Тестирование

```bash
python manage.py test
```

Тесты покрывают CRUD, фильтрацию по стране/городу, сортировку, вычисление
уровня иерархии, защиту от циклов, read-only задолженности, права доступа
(аноним / неактивный / не-сотрудник / удалённый), вход в админку по email,
мягкое удаление и восстановление пользователя, `ALLOWED_HOSTS` и элементы
админ-панели.

## Линтеры

```bash
flake8 .
```

## Лицензия

[MIT](LICENSE)
