import traceback
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from bot.database.requests.logs import add_log



class LogsMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        try:
            if isinstance(event, Message):
                await add_log(user_id=event.from_user.id, message=f"Сообщение от пользователя", data=event.text or '')
            elif isinstance(event, CallbackQuery):
                await add_log(user_id=event.from_user.id, message=f"Callback от пользователя", data=event.data or '')
            else:
                await add_log(user_id=event.from_user.id, message=f"Неизвестное действие от пользователя", data=event)
        except Exception as e:
            traceback.print_exc()
        return await handler(event, data)
