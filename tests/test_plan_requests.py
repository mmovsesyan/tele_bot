import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from bot.database.requests.plan_requests import (
    create_plan_request,
    get_pending_requests,
    get_request_by_id,
    approve_request,
    reject_request,
)


@pytest.mark.asyncio
async def test_create_plan_request():
    mock_session = MagicMock()
    mock_req = MagicMock()
    mock_req.id = 1
    mock_req.user_id = 123
    mock_req.plan_uid = "standard"
    mock_req.type_ = "default"
    mock_req.status = "pending"

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    with patch("bot.database.requests.plan_requests.async_session", return_value=mock_session):
        # async context manager mock
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        # We need to capture the PlanRequest instance passed to add
        added_instances = []
        def capture_add(instance):
            added_instances.append(instance)
            # simulate id assignment after flush
            instance.id = 1
        mock_session.add = capture_add

        req = await create_plan_request(123, "standard", "default")

    assert len(added_instances) == 1
    instance = added_instances[0]
    assert instance.user_id == 123
    assert instance.plan_uid == "standard"
    assert instance.type_ == "default"
    assert instance.status == "pending"


@pytest.mark.asyncio
async def test_get_pending_requests():
    mock_req1 = MagicMock()
    mock_req1.user_id = 111
    mock_req1.status = "pending"
    mock_req2 = MagicMock()
    mock_req2.user_id = 222
    mock_req2.status = "pending"

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.__iter__ = lambda self: iter([mock_req1, mock_req2])
    mock_session.scalars = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("bot.database.requests.plan_requests.async_session", return_value=mock_session):
        requests = await get_pending_requests()

    assert len(requests) == 2
    assert requests[0].user_id == 111
    assert requests[1].user_id == 222


@pytest.mark.asyncio
async def test_approve_and_reject_request():
    mock_session = MagicMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("bot.database.requests.plan_requests.async_session", return_value=mock_session):
        await approve_request(1)
        await reject_request(2)

    assert mock_session.execute.call_count == 2
    assert mock_session.commit.call_count == 2
