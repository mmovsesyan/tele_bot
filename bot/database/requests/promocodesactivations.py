from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import async_session, PromocodeActivation


async def get_promocodeactivations():
    async with async_session() as session:
        result = await session.scalars(select(PromocodeActivation))
        return result


async def add_promocodeactivation(**kwargs) -> PromocodeActivation:
    async with async_session() as session:
        try:
            promocode = PromocodeActivation(**kwargs)
            session.add(promocode)
            await session.flush()
            session.expunge_all()
            await session.commit()
            return promocode
        except SQLAlchemyError as e:
            await session.rollback()
            raise e


async def get_promocode_activation_by_user_id(user_id: int, promo_id) -> PromocodeActivation:
    async with async_session() as session:
        result = await session.scalar(select(PromocodeActivation).where(and_(PromocodeActivation.user_id == user_id, PromocodeActivation.promo_id == promo_id)))
        return result


async def update_promocodeactivations(value: int, **kwargs):
    async with async_session() as session:
        await session.execute(update(PromocodeActivation).where(PromocodeActivation.value == value).values(**kwargs))
        await session.commit()
