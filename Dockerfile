FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements_linux.txt .
RUN pip install --no-cache-dir -r requirements_linux.txt

# Копируем проект
COPY . .

# Создаем директории
RUN mkdir -p config backups temp

# Entrypoint для автоинициализации
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
