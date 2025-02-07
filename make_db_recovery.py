import asyncio
from bot.utils.db_recovery import backup_database, schedule_backup


if __name__ == "__main__":
    backup_database()


# if __name__ == "__main__":
#     schedule_backup()