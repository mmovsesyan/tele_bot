import os
import traceback
import uuid
from datetime import datetime
from io import BytesIO
from typing import List

from openpyxl import Workbook

from bot.database.models import User
from bot.utils.config import ADMIN_IDS


def write_error(error: Exception):
    def generate_unique_uuid_file(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

        while True:
            file_uuid = str(uuid.uuid4())
            file_path = os.path.join(directory, f"{file_uuid}.txt")
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(file_uuid)
                return file_path

    os.makedirs("errors", exist_ok=True)

    filename = generate_unique_uuid_file("errors")

    error_text = "".join((traceback.format_exception(None, error, error.__traceback__)))

    with open(filename, "w", encoding="utf-8") as file:
        file.write(error_text)

    return filename


def generate_users_xlsx(users: List[User]) -> BytesIO:
    output = BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Пользователи"

    headers = [
        "ID",
        "ID пользователя",
        "Имя пользователя",
        "Полное имя",
        "План",
        "Дата окончания плана",
        "Приглашён кем",
        "Приглашено в этом месяце",
        "Автоплатеж",
        "Текущая модель",
        "Заблокирован",
        "Администратор"
    ]
    ws.append(headers)

    for user in users:
        row = [
            user.id,
            user.user_id,
            user.username if user.username else "Не указан",
            user.full_name,
            user.plan,
            format_datetime(user.plan_due_to),
            user.invited_by if user.invited_by else "Нет",
            user.invited_this_month,
            "Включена" if user.auto_payment else "Отключена",
            user.current_model,
            "Да" if user.is_blocked else "Нет",
            "Да" if (user.is_admin or user.user_id in ADMIN_IDS) else "Нет"
        ]
        ws.append(row)

    wb.save(output)
    output.seek(0)
    return output


def format_datetime(dt: datetime) -> str:
    return dt.strftime('%d.%m.%Y') if dt else 'Нет'
