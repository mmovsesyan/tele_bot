from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import Promocode, async_session


async def get_promocodes():
    async with async_session() as session:
        result = await session.scalars(select(Promocode))
        return result


async def add_promocode(**kwargs) -> Promocode:
    async with async_session() as session:
        try:
            promocode = Promocode(**kwargs)
            session.add(promocode)
            await session.flush()
            session.expunge_all()
            await session.commit()
            return promocode
        except SQLAlchemyError as e:
            await session.rollback()
            raise e


async def get_promocode_by_name(value: str) -> Promocode:
    async with async_session() as session:
        result = await session.scalar(select(Promocode).where(Promocode.value == value))
        return result


async def update_promocode(value: int, **kwargs):
    async with async_session() as session:
        await session.execute(
            update(Promocode).where(Promocode.value == value).values(**kwargs)
        )
        await session.commit()
