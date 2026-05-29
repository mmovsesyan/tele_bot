#!/bin/sh
set -e

CONFIG_DIR="/app/config"
CONFIG_FILE="$CONFIG_DIR/config.yml"
EXAMPLE_DIR="/app/config_example"

# Копирование тарифных планов, если их нет
for fname in plans.json; do
    if [ ! -f "$CONFIG_DIR/$fname" ]; then
        if [ -f "$EXAMPLE_DIR/$fname" ]; then
            cp "$EXAMPLE_DIR/$fname" "$CONFIG_DIR/$fname"
            echo "[entrypoint] Copied $fname"
        else
            echo "[entrypoint] Warning: $fname not found in $EXAMPLE_DIR"
        fi
    fi
done

# Если конфиг отсутствует — запускаем интерактивный setup
if [ ! -f "$CONFIG_FILE" ]; then
    echo "============================================================"
    echo "  Конфиг не найден. Запуск интерактивной настройки..."
    echo "============================================================"
    python /app/setup.py
    echo ""
    echo "[entrypoint] Конфиг создан. Инициализация..."
fi

# Ожидание доступности PostgreSQL
echo "[entrypoint] Waiting for PostgreSQL..."
python -c "
import os, time, psycopg2
host = os.getenv('SQLALCHEMY_IP', 'db')
port = os.getenv('SQLALCHEMY_PORT', '5432')
user = os.getenv('SQLALCHEMY_USER', 'postgres')
password = os.getenv('SQLALCHEMY_PASSWORD', 'postgres')
dbname = os.getenv('SQLALCHEMY_DB_NAME', 'tgbot')
for _ in range(60):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
        print('[entrypoint] PostgreSQL is ready.')
        break
    except Exception:
        time.sleep(1)
else:
    print('[entrypoint] PostgreSQL did not become ready in time.')
    exit(1)
"

# Автоинициализация БД через SQLAlchemy
echo "[entrypoint] Running database initialization..."
python -c "
import asyncio
from bot.database.models import on_startup_database
asyncio.run(on_startup_database())
print('[entrypoint] Database initialized.')
"

# Запуск бота
exec python /app/main.py
