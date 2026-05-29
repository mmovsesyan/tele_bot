#!/usr/bin/env python3
"""
Интерактивная установка и настройка Tele Bot.
Запуск: python setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_header(title: str):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_step(n: int, total: int, text: str):
    print(f"\n[{n}/{total}] {text}")


def ask(question: str, default: str = "") -> str:
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "
    answer = input(prompt).strip()
    return answer if answer else default


def ask_yes_no(question: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    answer = input(question + suffix).strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes", "д", "да")


def check_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_pip_install(req_file: str):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка установки зависимостей: {e}")
        return False


def write_config(config_dir: Path, data: dict):
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.yml"

    lines = [
        "# Токен телеграм бота",
        f"TG_TOKEN: {data['tg_token']}",
        "",
        "# PostgreSQL",
        f"SQLALCHEMY_DB_NAME: {data['db_name']}",
        f"SQLALCHEMY_IP: {data['db_ip']}",
        f"SQLALCHEMY_PORT: {data['db_port']}",
        f"SQLALCHEMY_USER: {data['db_user']}",
        f"SQLALCHEMY_PASSWORD: {data['db_password']}",
        "",
        "# Администраторы (через пробел)",
        f"ADMIN_IDS: {data['admin_ids']}",
        "",
        "# Ollama Cloud (основные текстовые модели)",
        f"OLLAMA_API_KEY: {data['ollama_api_key']}",
        f"OLLAMA_BASE_URL: {data['ollama_base_url']}",
        f"OLLAMA_GPT_MODEL: {data['ollama_gpt_model']}",
        f"OLLAMA_QWEN_MODEL: {data['ollama_qwen_model']}",
        f"OLLAMA_CLAUDE_MODEL: {data['ollama_claude_model']}",
        f"OLLAMA_ADMIN_MODEL: {data['ollama_admin_model']}",
        "",
        "# OpenAI (только для Whisper)",
        f"OPENAI_API_KEY: {data['openai_api_key']}",
        f"OPENAI_ADMIN_MODEL: {data['openai_admin_model']}",
        f"OPENAI_ADMIN_TOKEN_LIMIT: {data['openai_admin_token_limit']}",
        "",
        "# Qwen legacy (оставлено для совместимости конфига)",
        f"QWEN_API_KEY: {data['qwen_api_key']}",
        "",
        "# Anthropic legacy (оставлено для совместимости конфига)",
        f"ANTHROPIC_API_KEY: {data['anthropic_api_key']}",
        "",
        "# Системные настройки",
        f"TIMEZONE: {data['timezone']}",
        f"REDIS_HOST: {data['redis_host']}",
        f"REDIS_DB: {data['redis_db']}",
    ]

    config_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nКонфиг сохранён: {config_path.resolve()}")


def copy_plans(src_dir: Path, dst_dir: Path):
    for fname in ("plans.json",):
        src = src_dir / fname
        dst = dst_dir / fname
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Скопирован {fname}")
        else:
            print(f"  ⚠ {fname} не найден в {src_dir}")


def main():
    in_docker = Path("/.dockerenv").exists()
    project_dir = Path(__file__).parent.resolve()
    config_dir = project_dir / "config"
    config_example_dir = project_dir / "config_example"

    print_header("Tele Bot — Интерактивная установка")
    print("\nЭтот скрипт поможет настроить бот с нуля.")
    print("Все значения можно изменить позже в config/config.yml")

    if not ask_yes_no("Продолжить установку?", default=True):
        print("Установка отменена.")
        sys.exit(0)

    # ── Step 1: Зависимости ──
    print_step(1, 5, "Установка зависимостей")
    if in_docker:
        print("  Работаем внутри Docker — зависимости уже установлены. Пропускаем.")
    else:
        platform = sys.platform
        req_file = "requirements_linux.txt" if platform != "win32" else "requirements_windows.txt"
        if ask_yes_no(f"Установить зависимости из {req_file}?", default=True):
            if not check_command("pip"):
                print("⚠ pip не найден. Пропускаем.")
            else:
                run_pip_install(req_file)
        else:
            print("Пропущено.")

    # ── Step 2: Конфигурация ──
    print_step(2, 5, "Настройка конфигурации")

    print("\n--- Telegram ---")
    tg_token = ask("Токен бота (от @BotFather)")

    print("\n--- База данных PostgreSQL ---")
    db_name = ask("Имя БД", "tgbot")
    db_ip = ask("Хост БД", "db" if in_docker else "localhost")
    db_port = ask("Порт БД", "5432")
    db_user = ask("Пользователь БД", "postgres")
    db_password = ask("Пароль БД", "postgres" if in_docker else "1")

    print("\n--- Redis ---")
    redis_host = ask("Порт Redis", "6379")
    redis_db = ask("Номер БД Redis", "0")

    print("\n--- Администраторы ---")
    admin_ids = ask("Telegram ID админов (через пробел)", "123 321")

    print("\n--- Ollama Cloud (основной AI) ---")
    ollama_api_key = ask("Ollama API Key", "sk-ollama-")
    ollama_base_url = ask("Ollama Base URL", "https://api.ollama.com/v1")
    ollama_gpt_model = ask("Модель GPT (Ollama)", "gpt-oss:20b-cloud")
    ollama_qwen_model = ask("Модель Qwen (Ollama)", "qwen3.5:cloud")
    ollama_claude_model = ask("Модель Claude (Ollama)", "qwen3-coder-next:cloud")
    ollama_admin_model = ask("Админ модель (Ollama)", "kimi-k2.6:cloud")

    print("\n--- OpenAI (только для Whisper) ---")
    openai_api_key = ask("OpenAI API Key", "sk-proj-")
    openai_admin_model = ask("OpenAI админ модель", "gpt-4o")
    openai_admin_token_limit = ask("OpenAI лимит токенов для админа", "")

    print("\n--- Legacy keys (оставьте пустыми если не нужны) ---")
    qwen_api_key = ask("Qwen API Key", "")
    anthropic_api_key = ask("Anthropic API Key", "")

    print("\n--- Системные настройки ---")
    timezone = ask("Таймзона", "Europe/Moscow")

    data = {
        "tg_token": tg_token,
        "db_name": db_name,
        "db_ip": db_ip,
        "db_port": db_port,
        "db_user": db_user,
        "db_password": db_password,
        "redis_host": redis_host,
        "redis_db": redis_db,
        "admin_ids": admin_ids,
        "ollama_api_key": ollama_api_key,
        "ollama_base_url": ollama_base_url,
        "ollama_gpt_model": ollama_gpt_model,
        "ollama_qwen_model": ollama_qwen_model,
        "ollama_claude_model": ollama_claude_model,
        "ollama_admin_model": ollama_admin_model,
        "openai_api_key": openai_api_key,
        "openai_admin_model": openai_admin_model,
        "openai_admin_token_limit": openai_admin_token_limit,
        "qwen_api_key": qwen_api_key,
        "anthropic_api_key": anthropic_api_key,
        "timezone": timezone,
    }

    write_config(config_dir, data)

    # ── Step 3: JSON планы ──
    print_step(3, 5, "Копирование тарифных планов")
    copy_plans(config_example_dir, config_dir)

    # ── Step 4: Инициализация БД ──
    print_step(4, 5, "Инициализация базы данных")
    if in_docker:
        print("  Работаем внутри Docker — БД будет инициализирована автоматически. Пропускаем.")
    else:
        if ask_yes_no("Создать/обновить таблицы в PostgreSQL?", default=True):
            try:
                from bot.database.models import on_startup_database
                import asyncio
                asyncio.run(on_startup_database())
                print("База данных инициализирована.")
            except Exception as e:
                print(f"⚠ Ошибка инициализации БД: {e}")
                print("Убедитесь, что PostgreSQL запущен и параметры верны.")
        else:
            print("Пропущено.")

    # ── Step 5: Финал ──
    print_step(5, 5, "Готово")
    print_header("Установка завершена")
    print(f"\nКонфиг:     {config_dir / 'config.yml'}")
    if in_docker:
        print(f"\nDocker: бот запустится автоматически после настройки.")
    else:
        print(f"Запуск:     python main.py")
    print(f"\nПолезные команды:")
    if not in_docker:
        print(f"  python main.py              # Запуск бота")
        print(f"  python setup.py             # Перенастройка")
    print(f"  python make_db_recovery.py  # Бэкап БД")
    print("\nУдачи! 🤖")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nУстановка прервана.")
        sys.exit(1)
