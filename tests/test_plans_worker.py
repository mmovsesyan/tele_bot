import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from bot.utils.plans_worker import give_plan, refresh_requests


@pytest.mark.asyncio
async def test_give_plan_standard():
    mock_plans = [
        {"uid": "standard", "name": "Стандарт", "price": 1000, "duration_days": 30,
         "day_reqs": {"gpt": 15, "claude": 15, "qwen": 15}},
    ]

    with patch("bot.utils.plans_worker.json_worker.read", new=AsyncMock(return_value=mock_plans)):
        with patch("bot.utils.plans_worker.update_user", new=AsyncMock()) as mock_update:
            plan = await give_plan(123, "standard", None)

    assert plan["uid"] == "standard"
    assert plan["price"] == 1000
    mock_update.assert_awaited_once()
    kwargs = mock_update.call_args.kwargs
    assert kwargs["plan"] == "standard"
    assert kwargs["request_remains"]["gpt"] == 15
    # plan_due_to should be ~30 days from now
    assert kwargs["plan_due_to"] is not None
    assert (kwargs["plan_due_to"] - datetime.now()).days >= 29


@pytest.mark.asyncio
async def test_give_plan_free_hours():
    mock_plans = [
        {"uid": "free", "name": "Бесплатный", "price": 0, "duration_hours": 12,
         "day_reqs": {"gpt": 5, "claude": 5, "qwen": 5}},
    ]

    with patch("bot.utils.plans_worker.json_worker.read", new=AsyncMock(return_value=mock_plans)):
        with patch("bot.utils.plans_worker.update_user", new=AsyncMock()) as mock_update:
            plan = await give_plan(456, "free", None)

    assert plan["uid"] == "free"
    kwargs = mock_update.call_args.kwargs
    due_to = kwargs["plan_due_to"]
    delta = due_to - datetime.now()
    assert delta.total_seconds() <= 12 * 3600
    assert delta.total_seconds() > 11 * 3600


@pytest.mark.asyncio
async def test_refresh_requests():
    mock_plans = [
        {"uid": "premium", "name": "Премиум", "price": 2000, "duration_days": 30,
         "day_reqs": {"gpt": 30, "claude": 30, "qwen": 30}},
    ]

    mock_user = MagicMock()
    mock_user.user_id = 789
    mock_user.plan = "premium"

    with patch("bot.utils.plans_worker.json_worker.read", new=AsyncMock(return_value=mock_plans)):
        with patch("bot.utils.plans_worker.update_user", new=AsyncMock()) as mock_update:
            await refresh_requests(mock_user)

    mock_update.assert_awaited_once_with(
        789,
        request_remains={"gpt": 30, "claude": 30, "qwen": 30},
    )
