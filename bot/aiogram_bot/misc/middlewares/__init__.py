from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from bot.aiogram_bot.misc.middlewares.admin_middleware import IsAdminMiddleware
from bot.aiogram_bot.misc.middlewares.antiflood_middleware import AntiFloodMiddleware
from bot.aiogram_bot.misc.middlewares.check_user_db_middleware import DBMiddleware
from bot.aiogram_bot.misc.middlewares.is_private_middleware import IsPrivateMiddleware
from bot.aiogram_bot.misc.middlewares.logs_middleware import LogsMiddleware
from bot.aiogram_bot.misc.middlewares.media_middleware import MediaMiddleware
from bot.aiogram_bot.misc.middlewares.queue_middleware import QueueMessagesMiddleware

admin_middleware = IsAdminMiddleware()


def include_middlewares(router, middleware):
    router.message.middleware(middleware)
    router.callback_query.middleware(middleware)


def register_middlewares(dp: Dispatcher):
    dp.message.middleware(IsPrivateMiddleware())
    dp.message.middleware(MediaMiddleware())
    dp.message.middleware(LogsMiddleware())
    dp.message.middleware(AntiFloodMiddleware())
    dp.message.middleware(QueueMessagesMiddleware())
    dp.message.middleware(DBMiddleware())

    dp.callback_query.middleware(LogsMiddleware())
    dp.callback_query.middleware(AntiFloodMiddleware())
    dp.callback_query.middleware(QueueMessagesMiddleware())
    dp.callback_query.middleware(DBMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())
