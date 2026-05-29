from sqlalchemy import select, update

from bot.database.models import async_session, PlanRequest


async def create_plan_request(user_id: int, plan_uid: str, type_: str = 'default'):
    async with async_session() as session:
        req = PlanRequest(user_id=user_id, plan_uid=plan_uid, type_=type_, status='pending')
        session.add(req)
        await session.commit()
        await session.refresh(req)
        return req


async def get_pending_requests():
    async with async_session() as session:
        result = await session.scalars(select(PlanRequest).where(PlanRequest.status == 'pending'))
        return [r for r in result]


async def get_request_by_id(request_id: int):
    async with async_session() as session:
        return await session.scalar(select(PlanRequest).where(PlanRequest.id == request_id))


async def approve_request(request_id: int):
    async with async_session() as session:
        await session.execute(
            update(PlanRequest).where(PlanRequest.id == request_id).values(status='approved')
        )
        await session.commit()


async def reject_request(request_id: int):
    async with async_session() as session:
        await session.execute(
            update(PlanRequest).where(PlanRequest.id == request_id).values(status='rejected')
        )
        await session.commit()
