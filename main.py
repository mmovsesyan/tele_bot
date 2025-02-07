import asyncio
import logging
import sys

from bot.aiogram_bot.app import aiogram_start

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(aiogram_start())
    except KeyboardInterrupt:
        print("Goodbye!")
