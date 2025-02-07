from aiogram import Bot
from aiogram.types import BotCommand

from bot.texts import START_DESCRIPTION


async def create_bot_commands(bot: Bot):
    await bot.set_my_commands(
        commands=[BotCommand(command='/start', description=START_DESCRIPTION)]
    )