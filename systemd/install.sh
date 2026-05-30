#!/bin/bash
set -e

SERVICE_NAME="telebot.service"
SERVICE_SRC="$(dirname "$0")/$SERVICE_NAME"
SERVICE_DST="/etc/systemd/system/$SERVICE_NAME"

echo "============================================================"
echo "  Установка systemd сервиса Tele Bot"
echo "============================================================"

if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: запустите скрипт с sudo"
    exit 1
fi

if [ ! -f "$SERVICE_SRC" ]; then
    echo "Ошибка: $SERVICE_NAME не найден в $(dirname "$0")"
    exit 1
fi

read -rp "Рабочая директория бота [/opt/tele_bot]: " WORKDIR
WORKDIR=${WORKDIR:-/opt/tele_bot}

if [ ! -d "$WORKDIR" ]; then
    echo "Ошибка: директория $WORKDIR не существует"
    exit 1
fi

read -rp "Пользователь для запуска [telebot]: " USERNAME
USERNAME=${USERNAME:-telebot}

if ! id "$USERNAME" &>/dev/null; then
    echo "Пользователь $USERNAME не найден. Создаём..."
    useradd -r -s /bin/false "$USERNAME"
    chown -R "$USERNAME:$USERNAME" "$WORKDIR"
fi

read -rp "Путь к venv python [$WORKDIR/venv/bin/python]: " PYTHON_PATH
PYTHON_PATH=${PYTHON_PATH:-$WORKDIR/venv/bin/python}

if [ ! -f "$PYTHON_PATH" ]; then
    echo "Ошибка: python не найден по пути $PYTHON_PATH"
    exit 1
fi

cp "$SERVICE_SRC" "$SERVICE_DST"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$WORKDIR|" "$SERVICE_DST"
sed -i "s|User=.*|User=$USERNAME|" "$SERVICE_DST"
sed -i "s|Group=.*|Group=$USERNAME|" "$SERVICE_DST"
sed -i "s|Environment=PATH=.*|Environment=PATH=$(dirname "$PYTHON_PATH")|" "$SERVICE_DST"
sed -i "s|ExecStart=.*|ExecStart=$PYTHON_PATH $WORKDIR/main.py|" "$SERVICE_DST"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo ""
echo "✅ Сервис установлен: $SERVICE_DST"
echo "   Команды управления:"
echo "     sudo systemctl start $SERVICE_NAME   # запуск"
echo "     sudo systemctl stop $SERVICE_NAME    # остановка"
echo "     sudo systemctl status $SERVICE_NAME  # статус"
echo "     sudo systemctl restart $SERVICE_NAME # перезапуск"
echo ""
echo "   Логи:"
echo "     sudo journalctl -u $SERVICE_NAME -f"
