from datetime import timedelta, datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message

from bot.database.models import User
from bot.database.requests.users import add_user, update_user, get_user

from bot.texts import REF_INVITED_TXT
from bot.utils.plans_worker import give_plan


async def get_referal(user_id: int, text: str):
    user = await get_user(user_id)
    if user:
        return

    if text.startswith("/start r"):
        ref_id = text.split(" ")[-1][1:]
        if ref_id.isdigit():
            return int(ref_id)


async def process_referal(bot: Bot, refv_user: User, invited_user_id):
    invited_user = await get_user(invited_user_id)
    if invited_user:
        return
    if refv_user.invited_this_month < 7:
        try:
            await bot.send_message(refv_user.user_id, text=REF_INVITED_TXT, parse_mode='HTML')
        except:
            ...
        if not refv_user.plan_due_to:
            await give_plan(refv_user.user_id, 'trial', (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y"))
            await update_user(refv_user.user_id, invited_this_month=refv_user.invited_this_month + 1)
        else:
            await update_user(refv_user.user_id, plan_due_to=refv_user.plan_due_to + timedelta(days=1), invited_this_month=refv_user.invited_this_month + 1)
        return True
    await update_user(refv_user.user_id,
                      invited_this_month=refv_user.invited_this_month + 1)

    return False
class DBMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if hasattr(event, 'from_user'):
            ref_id = None
            if isinstance(event, Message):
                ref_id = await get_referal(event.from_user.id, event.text)
                if ref_id:
                    refv_user = await get_user(ref_id)
                    if refv_user:
                        await process_referal(event.bot, refv_user, event.from_user.id)
            user = await add_user(
                user_id=event.from_user.id,
                username=event.from_user.username,
                full_name=event.from_user.full_name,
                invited_by=ref_id,
            )
            if ref_id:
                await give_plan(event.from_user.id, 'trial', (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y"))
                data['first_meeting'] = True

            if user.full_name != event.from_user.full_name or user.username != event.from_user.username:
                user = await update_user(
                    user_id=event.from_user.id,
                    full_name=event.from_user.full_name,
                    username=event.from_user.username,
                    is_returnable=True,
                )
            data['user'] = user
        return await handler(event, data)
