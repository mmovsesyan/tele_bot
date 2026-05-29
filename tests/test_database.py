import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path

# We need to mock config before importing models
config_mock = MagicMock()
config_mock.SQLALCHEMY_URL = "sqlite+aiosqlite:///:memory:"
config_mock.SQLALCHEMY_DB_NAME = "test"
config_mock.SQLALCHEMY_USER = "test"
config_mock.SQLALCHEMY_PASSWORD = "test"
config_mock.SQLALCHEMY_IP = "localhost"
config_mock.SQLALCHEMY_PORT = "5432"

sys.modules["bot.utils.config"] = config_mock

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, Boolean, JSON


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column()
    request_remains = mapped_column(JSON())
    plan: Mapped[str] = mapped_column()
    plan_due_to = mapped_column(DateTime(), nullable=True)
    invited_by = mapped_column(BigInteger, nullable=True)
    invited_this_month = mapped_column(BigInteger, default=0)
    auto_payment = mapped_column(Boolean, default=False)
    current_model: Mapped[str] = mapped_column(default='gpt')
    is_blocked = mapped_column(Boolean, default=False)
    is_admin = mapped_column(Boolean, default=False)
    image_gens = mapped_column(BigInteger, default=0)
    video_gens = mapped_column(BigInteger, default=0)


class PlanRequest(Base):
    __tablename__ = 'plan_requests'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    plan_uid: Mapped[str] = mapped_column()
    type_: Mapped[str] = mapped_column(default='default')
    status: Mapped[str] = mapped_column(default='pending')
    created_at = mapped_column(DateTime())


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine)
    yield async_session
    await engine.dispose()


@pytest.mark.asyncio
async def test_user_model(db_session):
    async with db_session() as session:
        user = User(
            user_id=123456,
            username="testuser",
            full_name="Test User",
            request_remains={"gpt": 5, "claude": 5, "qwen": 5},
            plan="free",
            plan_due_to=datetime.now() + timedelta(hours=12),
        )
        session.add(user)
        await session.commit()

        result = await session.get(User, 1)
        assert result.user_id == 123456
        assert result.username == "testuser"
        assert result.plan == "free"
        assert result.request_remains["gpt"] == 5


@pytest.mark.asyncio
async def test_plan_request_model(db_session):
    async with db_session() as session:
        req = PlanRequest(
            user_id=123456,
            plan_uid="standard",
            type_="default",
            status="pending",
            created_at=datetime.utcnow(),
        )
        session.add(req)
        await session.commit()

        result = await session.get(PlanRequest, 1)
        assert result.user_id == 123456
        assert result.plan_uid == "standard"
        assert result.status == "pending"
