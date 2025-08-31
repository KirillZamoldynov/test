# API Service

REST API сервис для управления вопросами и ответами

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)
![docker](https://img.shields.io/badge/docker-ready-blue.svg)


## Описание проекта

Web-API для системы вопросов и ответов, реализованный на FastAPI. Предоставляет полный CRUD функционал для работы с вопросами и ответами, включает валидацию данных, каскадное удаление, миграции БД и тестирование.

## Технический стек

- **Backend**: FastAPI 0.116+ (Python 3.11+)
- **База данных**: PostgreSQL 16 + SQLAlchemy 2.0 (async ORM)
- **Миграции**: Alembic
- **Тестирование**: Pytest
- **Контейнеризация**: Docker + Docker Compose
- **Валидация**: Pydantic v2

## Структура проекта

```
├── app/
│   ├── api/
│   │   ├── dependencies.py     # Зависимости FastAPI
│   │   └── endpoints/
│   │       ├── answers.py      # API для ответов
│   │       ├── health.py       # Служебные эндпоинты
│   │       └── questions.py    # API для вопросов
│   ├── models/
│   │   ├── base.py            # Базовая модель
│   │   └── models.py          # Модели SQLAlchemy
│   ├── schemas/
│   │   └── schemas.py         # Pydantic схемы валидации
│   ├── utils/
│   │   └── logger.py          # Конфигурация логирования
│   ├── config.py              # Настройки приложения
│   ├── database.py            # Подключение к БД
│   └── main.py                # Основное приложение
├── tests/
│   ├── conftest.py            # Настройки pytest
│   └── api_test.py            # Тесты API
├── migration/
│   ├── versions/               # Файлы миграций
│   └── env.py                 # Конфигурация Alembic
├── alembic.ini                # Настройки миграций
├── docker-compose.yaml        # Docker Compose конфигурация
├── Dockerfile                 # Docker образ
├── entrypoint.sh              # Скрипт запуска контейнера
├── env.example                # Пример переменных окружения
└── requirements.txt           # Python зависимости
```

## Модели данных

### Question
- `id`: int - уникальный идентификатор
- `text`: str - текст вопроса (1-1000 символов)
- `created_at`: datetime - дата создания

### Answer
- `id`: int - уникальный идентификатор  
- `question_id`: int - ссылка на вопрос
- `user_id`: str - идентификатор пользователя
- `text`: str - текст ответа (1-500 символов)
- `created_at`: datetime - дата создания

## Запуск проекта

### Требования
- Docker 20.0+
- Docker Compose 2.0+

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/KirillZamoldynov/test
cd test

# Создать файл переменных окружения
cp env.example .env

# Запустить сервисы
docker-compose up -d
```

API доступен по адресу: http://localhost:8000

### Документация API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Вопросы
| Метод | Endpoint | Описание | Код |
|-------|----------|----------|-----|
| GET | `/questions/` | Получить все вопросы | 200 |
| POST | `/questions/` | Создать новый вопрос | 201 |
| GET | `/questions/{id}` | Получить вопрос с ответами | 200 |
| DELETE | `/questions/{id}` | Удалить вопрос | 204 |

### Ответы
| Метод | Endpoint | Описание | Код |
|-------|----------|----------|-----|
| POST | `/questions/{id}/answers/` | Добавить ответ к вопросу | 201 |
| GET | `/answers/{id}` | Получить ответ | 200 |
| DELETE | `/answers/{id}` | Удалить ответ | 204 |

### Служебные
| Метод | Endpoint | Описание | Код |
|-------|----------|----------|-----|
| GET | `/live` | Проверка статуса | 200 |
| GET | `/ready` | Проверка готовности | 200 |
| GET | `/health` | Диагностика | 200 |



## Тестирование

```bash
# Запуск тестов
docker-compose exec app pytest

# Тесты с покрытием
docker-compose exec app pytest --cov=app
```


## Миграции

Применяются автоматически при запуске.

Создание новой миграции:
```bash
docker-compose exec app alembic revision --autogenerate -m "Описание"
```

