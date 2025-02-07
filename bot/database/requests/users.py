from typing import Union

from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError

from bot import AI, json_worker
from bot.ai.gpt import GPT
from bot.ai.qwen import Qwen
from bot.database.models import async_session, User
from bot.utils.json_worker import get_plan_by_name


async def get_users():
    async with async_session() as session:
        result = await session.scalars(select(User))
        return [r for r in result]


async def add_user(user_id: int, **kwargs) -> User:
    plans = await json_worker.read('config/plans.json')
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.user_id == user_id))
            if not user:
                kwargs['plan'] = 'free'
                kwargs['request_remains'] = get_plan_by_name(plans,'free')['day_reqs']
                user = User(user_id=user_id, **kwargs)
                session.add(user)
                await session.flush()
                session.expunge_all()
                await session.commit()
            return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise e


async def get_user(user_id):
    try:
        user_id = int(user_id)
        req = User.user_id == user_id
    except:
        req = User.username == user_id
    async with async_session() as session:
        result = await session.scalar(select(User).where(req))
        return result

async def get_users_count_invited_by(invited_by: int) -> int:
    async with async_session() as session:
        result = await session.scalar(select(func.count()).where(User.invited_by == invited_by))
        return result or 0


async def update_user(user_id: int, **kwargs):
    async with async_session() as session:
        await session.execute(update(User).where(User.user_id == user_id).values(**kwargs))
        await session.commit()

async def update_users_invited_this_m():
    async with async_session() as session:
        await session.execute(update(User).values(invited_this_month=0))
        await session.commit()

def get_user_txt(user: User):
    txt = f"{user.user_id} | {user.full_name}"
    if user.username:
        txt += f" | @{user.username}"

    return txt

def get_model(user: User) -> Union[GPT, Qwen]:
    return AI[user.current_model]