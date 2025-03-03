import asyncio

from bot import json_worker
from bot.database.requests.users import get_users, update_user
from bot.utils.json_worker import get_plan_by_name


async def add_claude():
    users = await get_users()
    json_ = await json_worker.read('config/plans.json')
    for user in users:
        plan = get_plan_by_name(json_, user.plan)
        user.request_remains['claude'] = plan['day_reqs']['claude']
        await update_user(user.user_id, request_remains=user.request_remains)



if __name__ == '__main__':
    asyncio.run(add_claude())