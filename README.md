# Tele Bot — AI Telegram Bot

Telegram-бот с диалогами через AI-модели (Ollama Cloud), генерацией изображений, тарифной системой и админ-панелью.

## Возможности

- **AI-диалоги** — переключение между GPT, Qwen и Claude (все через Ollama Cloud)
- **Голосовые сообщения** — распознавание речи через Whisper (OpenAI)
- **Генерация изображений** — DALL-E 3 (OpenAI)
- **Тарифная система** — 3 плана: Бесплатный (12 часов), Стандарт, Премиум
- **Одобрение тарифов админом** — заявки на покупку подтверждаются вручную через админ-панель
- **Админ-панель** — рассылка, управление пользователями, одобрение заявок, статистика
- **Реферальная система** — приглашения друзей
- **Docker** — полностью контейнеризован с PostgreSQL + Redis
- **Интерактивная установка** — один скрипт `setup.py` для локального или Docker-запуска

## Стек

- **Bot:** aiogram 3.x, Redis (FSM)
- **DB:** PostgreSQL 15, SQLAlchemy async
- **AI:** Ollama Cloud (GPT/Qwen/Claude), OpenAI (DALL-E + Whisper)
- **Deploy:** Docker + Docker Compose

## Тарифы

| План | Запросов/день | Длительность | Цена |
|------|--------------|--------------|------|
| Бесплатный | 5 на каждую модель | 12 часов | 0 ₽ |
| Стандарт | 15 на каждую модель | 30 дней | 1000 ₽ |
| Премиум | 30 на каждую модель | 30 дней | 2000 ₽ |

Пользователь может переключать модель в настройках. Лимиты привязаны к `request_remains` в БД и обновляются ежедневно в полночь.

## Установка

### Docker (рекомендуется)

```bash
# 1. Клонируй репозиторий
git clone <repo>
cd tele_bot

# 2. Запусти
docker compose up --build
```

При первом запуске контейнер запустит **интерактивный `setup.py`** — введи токен бота, API-ключи, выбери модели. После настройки бот стартует автоматически. При следующих запусках `setup.py` пропускается.

### Локально (без Docker)

```bash
# 1. Установи зависимости
pip install -r requirements_linux.txt

# 2. Запусти интерактивную настройку
python setup.py

# 3. Запусти бота
python main.py
```

## Конфигурация

Все настройки задаются через `setup.py` или вручную в `config/config.yml`.

Ключевые переменные окружения (для Docker):

```env
TG_TOKEN=your_telegram_bot_token
ADMIN_IDS=123 321
OLLAMA_API_KEY=sk-ollama-
OLLAMA_BASE_URL=https://api.ollama.com/v1
OLLAMA_GPT_MODEL=gpt-oss:20b-cloud
OLLAMA_QWEN_MODEL=qwen3.5:cloud
OLLAMA_CLAUDE_MODEL=qwen3-coder-next:cloud
OLLAMA_ADMIN_MODEL=kimi-k2.6:cloud
OPENAI_API_KEY=sk-proj-
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=tgbot
```

Полный шаблон — `.env.example`.

## Админ-панель

Пункт **💻 Администрация** доступен для пользователей из `ADMIN_IDS` или с флагом `is_admin`.

**Функции:**
- 📥 **Заявки на тарифы** — одобрение/отклонение заявок пользователей
- ✉ Рассылка всем пользователям
- 👥 Выдача админ-прав
- 📈 Статистика
- 📃 Выгрузка пользователей в Excel
- 👤 Информация по пользователю
- ⛔ Бан/разбан

## Архитектура

```
tele_bot/
├── bot/
│   ├── ai/                    # AI-провайдеры (GPT, Qwen, Claude)
│   ├── aiogram_bot/
│   │   ├── handlers/
│   │   │   ├── users/         # Юзер-хендлеры (диалог, тарифы, настройки)
│   │   │   └── admins/        # Админ-хендлеры (одобрение заявок, рассылка)
│   │   ├── markups/           # Клавиатуры
│   │   └── misc/              # Middleware, состояния, команды
│   ├── database/
│   │   ├── models.py          # SQLAlchemy модели (User, PlanRequest, Log)
│   │   └── requests/          # CRUD-запросы
│   ├── payments/              # (отключено — Ckassa убрана)
│   └── utils/                 # Конфиг, валюта, планы, бэкапы
├── config_example/            # Шаблоны конфига и тарифов
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh              # Автоинициализация БД + интерактивный setup
├── setup.py                   # Интерактивный установщик
└── main.py                    # Точка входа
```

## Тесты

```bash
pip install -r requirements_linux.txt
python3 -m pytest tests/ -v
```

Покрытие:
- AI-провайдеры (GPT с Ollama Cloud)
- JSON-работник и тарифные планы
- Утилиты (даты, экранирование Markdown)
- Работа с заявками на тарифы (CRUD + одобрение/отклонение)
- Логика выдачи планов (12 часов free / 30 дней paid)
- Модели БД (User, PlanRequest)

## Полезные команды

| Команда | Описание |
|---------|----------|
| `python main.py` | Запуск бота |
| `python setup.py` | Перенастройка конфигурации |
| `python make_db_recovery.py` | Бэкап PostgreSQL |
| `docker compose up --build` | Запуск в Docker |
| `docker compose down -v` | Полная очистка (с БД) |
| `python3 -m pytest tests/ -v` | Запуск тестов |

## Модели Ollama Cloud (по умолчанию)

- **GPT** — `gpt-oss:20b-cloud`
- **Qwen** — `qwen3.5:cloud`
- **Claude** — `qwen3-coder-next:cloud`
- **Admin** — `kimi-k2.6:cloud`

Модели можно сменить в `config/config.yml` или через `setup.py`.
