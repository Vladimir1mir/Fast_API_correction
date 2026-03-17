# Домашнее задание "Создание REST API на FastApi"

Сервис объявлений реализован на FastAPI. Основной сценарий запуска для сдачи задания: приложение и PostgreSQL через Docker Compose.

## Возможности API

- `POST /advertisement`
- `PATCH /advertisement/{advertisement_id}`
- `DELETE /advertisement/{advertisement_id}`
- `GET /advertisement/{advertisement_id}`
- `GET /advertisement`

## Структура объявления

- `title` — заголовок
- `description` — описание
- `price` — цена
- `author` — автор
- `date_of_creation` — дата создания

## Запуск через Docker

1. Запустите Docker Desktop.
2. Из корня проекта выполните:

```bash
docker compose up --build
```

3. После старта контейнеров откройте Swagger:

```text
http://localhost:8080/docs
```

API будет доступно на `http://localhost:8080`.

## Локальный запуск без Docker

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Убедитесь, что PostgreSQL доступен и переменные окружения соответствуют настройкам в `.env`.
3. Запустите приложение:

```bash
python run.py
```

Swagger для локального запуска будет доступен на:

```text
http://localhost:8000/docs
```

Скрипт `run.py` находится в корне проекта рядом с `app/` и использует переменные `APP_HOST` и `APP_PORT`, если нужно переопределить адрес или порт запуска.

## Запуск тестов

Установите зависимости для тестов:

```bash
pip install -r requirements_test.txt
```

Запустите тесты:

```bash
pytest -q
```

## Задание

Домашнее задание к лекции «Создание REST API на FastApi» часть 1.

Нужно реализовать сервис объявлений купли/продажи с полями:

- заголовок
- описание
- цена
- автор
- дата создания

Необходимые методы:

- Создание: `POST /advertisement`
- Обновление: `PATCH /advertisement/{advertisement_id}`
- Удаление: `DELETE /advertisement/{advertisement_id}`
- Получение по id: `GET /advertisement/{advertisement_id}`
- Поиск по полям: `GET /advertisement?{query_string}`
