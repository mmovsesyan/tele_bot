import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot.aiogram_bot.handlers.admins import mass_send
from bot.aiogram_bot.misc.create_commands import create_bot_commands
from bot.aiogram_bot.misc.middlewares import register_middlewares
from bot.database.models import on_startup_database
from bot.payments.ckassa.webhook import init_webhook_app
from bot.utils.config import TG_TOKEN, REDIS_HOST, REDIS_DB
from bot.utils.db_recovery import schedule_backup
from bot.utils.invited_this_m_worker import check_time_invited_m
from bot.utils.plans_worker import schedule_tariff_check


async def aiogram_on_startup(bot: Bot):
    await on_startup_database()

    bot_info = await bot.get_me()
    from bot.utils import config
    config.BOT_USERNAME = bot_info.username
    try:
        await create_bot_commands(bot)
    except:
        ...
    asyncio.create_task(schedule_tariff_check())
    asyncio.create_task(init_webhook_app(bot))
    asyncio.create_task(check_time_invited_m())
    asyncio.create_task(schedule_backup())
    logging.info("Bot has been started! -> @" + str(bot_info.username))


def register_routers(dp: Dispatcher):
    """
    Registering routers
    """

    from bot.aiogram_bot.handlers.users import menu
    from bot.aiogram_bot.handlers.users import tariffes
    from bot.aiogram_bot.handlers.users import switch_autopayment
    from bot.aiogram_bot.handlers.users import dialog
    from bot.aiogram_bot.handlers.users import enter_promo
    from bot.aiogram_bot.handlers.users import info
    from bot.aiogram_bot.handlers.users import ref
    from bot.aiogram_bot.handlers.users import settings
    from bot.aiogram_bot.handlers.admins import ban_user
    from bot.aiogram_bot.handlers.admins import create_promo
    from bot.aiogram_bot.handlers.admins import join_admin
    from bot.aiogram_bot.handlers.admins import stats
    from bot.aiogram_bot.handlers.admins import change_price
    from bot.aiogram_bot.handlers.admins import get_info
    from bot.aiogram_bot.handlers.admins import give_admin
    from bot.aiogram_bot.handlers.admins import upload_users
    from bot.aiogram_bot.handlers.users import get_offer
    from bot.aiogram_bot.handlers.users import video_gen
    dp.include_routers(
        dialog.router,
        menu.router,
        enter_promo.router,
        info.router,
        video_gen.router,
        ref.router,
        settings.router,
        switch_autopayment.router,
        get_offer.router,
        tariffes.router,

        ban_user.router,
        change_price.router,
        create_promo.router,
        get_info.router,
        give_admin.router,
        join_admin.router,
        mass_send.router,
        stats.router,
        upload_users.router,
    )


async def aiogram_start():
    bot = Bot(token=TG_TOKEN)

    redis = Redis(host="localhost", port=REDIS_HOST, db=REDIS_DB)
    storage = RedisStorage(redis=redis)

    dp = Dispatcher(storage=storage)

    register_middlewares(dp)
    register_routers(dp)
    await aiogram_on_startup(bot)
    await dp.start_polling(bot)
