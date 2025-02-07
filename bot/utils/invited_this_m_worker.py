import asyncio
import datetime

from bot.database.requests.users import update_users_invited_this_m


async def check_time_invited_m():
    while True:
        now = datetime.datetime.now()
        if now.day == 1 and now.hour == 0 and now.minute == 0:
            await update_users_invited_this_m()
            await asyncio.sleep(60)
        await asyncio.sleep(30)