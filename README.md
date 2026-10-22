<div align="center">

# 💊 chemist_app

**REST API подсистемы «Аптека»: склады, лекарства, списание, перемещение и отчёт о необходимости заказа**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.5-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## 📖 О проекте

Бэкенд подсистемы **«Аптека»** — часть FastAPI-приложения для управления лекарственными препаратами через мобильное приложение. Все операции доступны через REST API: учёт остатков по складам, поступления, списания (в том числе просроченных), перемещения между складами, заявки на выдачу и отчёт по необходимости заказа. Реализовано по техническому заданию, с дополнительной авторизацией пользователей.

## ✨ Возможности

| Задача из ТЗ | Что реализовано |
|---|---|
| Список лекарств и наличие на складах | каталог лекарств, записи «лекарство на складе», суммарное количество по всем складам |
| Поступление от поставщиков | регистрация записи на складе; просроченные препараты отклоняются (`409`) |
| Списание с причиной | списание позиции со склада с записью в таблицу списаний |
| Заявки на выдачу | создание заявки, просмотр, смена статуса (`pending` / `accepted` / `rejected`) |
| Перемещение между складами | проверка достаточности остатка, создание записи на целевом складе при необходимости |
| Отчёт по необходимости заказа | по каждому складу и лекарству: `sufficient` (≥100), `needs_order`, `urgent` (<20) |

Дополнительно:

- 🔐 авторизация по email/паролю: пароли хешируются (bcrypt), JWT выдаётся в `httponly`-cookie на 30 минут
- ⏰ автосписание просроченных лекарств — эндпоинт `GET /warehouse_medicine/check` и периодическая задача Celery
- 🧪 скрипт заполнения БД тестовыми данными

## 🧱 Стек

| Технология | Роль |
|---|---|
| FastAPI + Uvicorn | REST API |
| SQLAlchemy 2 (async) + aiosqlite | ORM, SQLite по умолчанию (`DB_URL`) |
| Alembic | миграции (`app/migration`) |
| Celery + Redis (+ Flower) | фоновые периодические задачи |
| python-jose, passlib, bcrypt | JWT и хеширование паролей |
| Pydantic Settings | конфигурация из `.env` |
| Docker Compose | контейнер Redis |

## 🗂 Структура проекта

```text
app/
├── main.py                 # создание FastAPI-приложения, подключение роутеров
├── config.py               # настройки из .env
├── database.py             # async-движок и сессии
├── dao/base.py             # базовый DAO
├── users/                  # регистрация, логин, JWT
├── medicines/              # справочник лекарств
├── warehouses/             # склады
├── warehouse_medicine/     # остатки на складах, перемещение, проверка просрочки
├── medicine_issuance/      # заявки на выдачу
├── core/                   # списание и отчёт по запасам
├── tasks/                  # Celery: приложение и периодическая задача
├── migration/              # окружение Alembic
└── create_test_data.py     # тестовые данные
open_api.yml                # выгрузка OpenAPI-схемы
docker-compose.yml          # Redis
```

## 🚀 Быстрый старт

```bash
git clone https://github.com/Edvvard0/chemist_app.git
cd chemist_app

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# создайте .env (список переменных — ниже)

docker compose up -d redis       # Redis для Celery

# схема БД: каталога versions в репозитории нет, создайте ревизию самостоятельно
alembic revision --autogenerate -m "init"
alembic upgrade head

python -m app.create_test_data   # (опционально) тестовые данные
uvicorn app.main:app --reload
```

Документация API (Swagger UI): `http://localhost:8000/docs`.

<details>
<summary>Фоновая проверка просрочки (Celery)</summary>

```bash
celery -A app.tasks.celery:celery worker --loglevel=info
celery -A app.tasks.celery:celery beat --loglevel=info
```

Расписание задано в `app/tasks/celery.py` (сейчас `crontab(minute="*/1")`, в комментарии указано «ежедневно в 00:00»). Брокер — `redis://localhost`.

</details>

## ⚙️ Конфигурация

Файл `.env` в корне проекта (`app/config.py`):

| Переменная | Назначение |
|---|---|
| `API_HOST`, `API_PORT` | хост и порт сервера |
| `DB_URL` | URL БД (необязательно; по умолчанию SQLite `data/db.sqlite3`) |
| `SECRET_KEY` | ключ подписи JWT |
| `ALGORITHM` | алгоритм подписи JWT |
| `REDIS_PASSWORD` | пароль Redis (docker-compose) |
| `REDIS_USER`, `REDIS_USER_PASSWORD` | пользователь Redis и его пароль (docker-compose) |

## 🔌 API

<details open>
<summary>Основные эндпоинты</summary>

| Группа | Эндпоинты |
|---|---|
| Users | `POST /users/login`, `POST /users/`, `GET /users/{user_id}`, `DELETE /users/{user_id}` |
| Medicine | `GET /medicine/`, `POST /medicine/`, `GET /medicine/{medicine_id}`, `DELETE /medicine/{medicine_id}` |
| Warehouses | `GET /warehouses/`, `POST /warehouses/`, `GET /warehouses/{warehouses_id}`, `DELETE /warehouses/{warehouses_id}` |
| WarehouseMedicine | `GET /warehouse_medicine/`, `POST /warehouse_medicine/`, `GET /warehouse_medicine/{wm_id}`, `DELETE /warehouse_medicine/{wm_id}`, `GET /warehouse_medicine/total/{medicine_id}`, `GET /warehouse_medicine/full_info/{wm_id}`, `GET /warehouse_medicine/check`, `POST /warehouse_medicine/transfer` |
| Core | `POST /core/` (списание), `GET /core/stock-report` (отчёт по запасам) |
| MedicineIssuance | `POST /med_issuance`, `GET /med_issuance{med_issuance_id}`, `POST /med_issuancestatus/{med_issuance_id}` |

</details>

Примеры тел запросов:

```bash
# списание: POST /core/
{"medicine_id": 1, "warehouses_id": 1, "reason": "Истек срок годности"}

# перемещение: POST /warehouse_medicine/transfer
{"medicine_id": 1, "from_warehouse_id": 1, "to_warehouse_id": 2, "quantity": 50}
```

Пример ответа `GET /core/stock-report`:

```json
{
  "warehouses": [
    {
      "warehouse_name": "Склад Москва",
      "warehouse_address": "Москва, ул. Ленина, 1",
      "medicines": [{"medicine_name": "Аспирин", "quantity": 100, "order_status": "sufficient"}]
    }
  ]
}
```

## 🗺 Планы

В исходной документации отмечено: автосписание через Celery планируется как замена ручному эндпоинту проверки просрочки (`/warehouse_medicine/check`).

## 👤 Автор

**Эдвард Осипчук** · GitHub [@Edvvard0](https://github.com/Edvvard0) · Telegram [@Edward0076](https://t.me/Edward0076)
