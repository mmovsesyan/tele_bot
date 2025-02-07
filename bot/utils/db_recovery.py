import asyncio
import os
import subprocess
import datetime
import time
from bot.utils.config import *

RETENTION_DAYS = 7
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_database():
    now = datetime.datetime.now(TIMEZONE)
    backup_filename = f"backup_{now.strftime('%Y-%m-%d_%H-%M-%S')}.sql"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    os.environ["PGPASSWORD"] = str(SQLALCHEMY_PASSWORD)
    dump_args = [
        "pg_dump", "-h", SQLALCHEMY_IP, "-p", str(SQLALCHEMY_PORT), "-U", SQLALCHEMY_USER,
        "-F", "c", "-b", "-v", "-f", backup_path, SQLALCHEMY_DB_NAME
    ]
    subprocess.run(dump_args, check=True)
    print(f"Создана резервная копия: {backup_path}")
    clean_old_backups()

def clean_old_backups():
    now = datetime.datetime.now(TIMEZONE)
    for filename in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, filename)
        if os.path.isfile(file_path) and filename.startswith("backup_"):
            file_time = datetime.datetime.strptime(filename[7:26], "%Y-%m-%d_%H-%M-%S")
            file_time = TIMEZONE.localize(file_time)
            if (now - file_time).days > RETENTION_DAYS:
                os.remove(file_path)
                print(f"Удален старый бэкап: {file_path}")

async def schedule_backup():
    while True:
        now = datetime.datetime.now(TIMEZONE)
        if now.strftime("%H:%M") == "22:00":
            try:
                backup_database()
            except Exception as e:
                print(f"Ошибка при создании резервной копии: {e}")
            await asyncio.sleep(60) 
        await asyncio.sleep(1) 


