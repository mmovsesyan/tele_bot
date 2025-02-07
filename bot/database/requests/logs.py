from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import Log, async_session


async def get_logs():
    async with async_session() as session:
        result = await session.scalars(select(Log))
        return result


async def add_log(**kwargs) -> Log:
    async with async_session() as session:
        try:
            log = Log(**kwargs)
            session.add(log)
            await session.flush()
            session.expunge_all()
            await session.commit()
            return log
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
