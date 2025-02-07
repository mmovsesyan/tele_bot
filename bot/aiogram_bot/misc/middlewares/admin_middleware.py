from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.utils.config import ADMIN_IDS


class IsAdminMiddleware(BaseMiddleware):

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message,
                       data: Dict[str, Any]) -> Any:
        user = data['user']
        if event.from_user.id not in ADMIN_IDS and not user.is_admin:
            return
        await handler(event, data)
