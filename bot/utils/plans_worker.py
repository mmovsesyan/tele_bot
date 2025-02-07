import asyncio
import traceback
from datetime import datetime
from datetime import timedelta

from bot import json_worker
from bot.database.models import User
from bot.database.requests.users import get_users, update_user
from bot.utils.config import TIMEZONE
from bot.utils.json_worker import get_plan_by_name


async def give_plan(user_id: int, p, date_to: str):
    user_id = int(user_id)
    json_ = await json_worker.read('config/plans.json')
    plan = get_plan_by_name(json_, p)
    if not date_to:
        date_to = datetime.now() + timedelta(days=30)
    elif date_to == 'del':
        date_to = None
    else:
        date_to = datetime.strptime(date_to, '%d.%m.%Y')
    await update_user(
        user_id,
        plan=p,
        plan_due_to=date_to,
        request_remains=plan['day_reqs'],
    )
    return plan


async def refresh_requests(user: User):
    user_id = user.user_id
    json_ = await json_worker.read('config/plans.json')
    plan = get_plan_by_name(json_, user.plan)
    await update_user(
        user_id,
        request_remains=plan['day_reqs'],
    )


async def check_tariff_updates():
    users = await get_users()
    now = datetime.now(TIMEZONE)

    for user in users:
        try:
            if user.plan_due_to is None:
                continue
            if now > user.plan_due_to.replace(tzinfo=TIMEZONE) and user.plan != 'free':
                free_plan = "free"
                await give_plan(user.user_id, free_plan, 'del')
            else:
                await refresh_requests(user)
        except Exception as e:
            traceback.print_exc()
            await asyncio.sleep(1)



async def schedule_tariff_check():
    while True:
        try:
            current_time = datetime.now(TIMEZONE)
            if current_time.hour == 0 and current_time.minute == 0:
                await check_tariff_updates()
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(1)

        except Exception:
            traceback.print_exc()
            await asyncio.sleep(1)

