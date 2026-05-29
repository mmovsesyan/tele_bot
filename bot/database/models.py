import asyncio
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Boolean, JSON
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from bot.database.ensure_db_created import create_database, auto_migrates
from bot.utils.config import SQLALCHEMY_URL, SQLALCHEMY_DB_NAME, SQLALCHEMY_USER, SQLALCHEMY_PASSWORD, SQLALCHEMY_PORT, \
    SQLALCHEMY_IP

engine = create_async_engine(SQLALCHEMY_URL, echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column()
    request_remains= mapped_column(JSON())
    plan: Mapped[str] = mapped_column()
    plan_due_to = mapped_column(DateTime(), nullable=True)
    invited_by = mapped_column(BigInteger, nullable=True)
    invited_this_month = mapped_column(BigInteger, default=0)
    auto_payment = mapped_column(Boolean, default=False)
    current_model: Mapped[str] = mapped_column(default='gpt')
    is_blocked = mapped_column(Boolean, default=False)
    is_admin = mapped_column(Boolean, default=False)



class Promocode(Base):
    __tablename__ = 'promocodes'

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column()
    sub_name: Mapped[str] = mapped_column(default='any')
    give_to = mapped_column(DateTime(), nullable=True)




class PromocodeActivation(Base):
    __tablename__ = 'promocodesactivations'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    promo_id = mapped_column(BigInteger)

class Log(Base):
    __tablename__ = 'logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger, nullable=True)
    message: Mapped[str] = mapped_column()
    data: Mapped[str] = mapped_column()


class PlanRequest(Base):
    __tablename__ = 'plan_requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    plan_uid: Mapped[str] = mapped_column()
    type_: Mapped[str] = mapped_column(default='default')
    status: Mapped[str] = mapped_column(default='pending')
    created_at = mapped_column(DateTime(), default=datetime.utcnow)


async def on_startup_database():
    create_database(SQLALCHEMY_DB_NAME, SQLALCHEMY_USER, SQLALCHEMY_PASSWORD, SQLALCHEMY_IP, SQLALCHEMY_PORT)
    auto_migrates(SQLALCHEMY_DB_NAME, SQLALCHEMY_USER, SQLALCHEMY_PASSWORD, SQLALCHEMY_IP, SQLALCHEMY_PORT)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(on_startup_database())
