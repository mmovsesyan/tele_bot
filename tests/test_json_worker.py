import json
import os
import pytest
import asyncio

from bot.utils.json_worker import AsyncJsonHandler, get_plan_by_name


@pytest.fixture
def sample_json(tmp_path):
    path = tmp_path / "plans.json"
    data = [
        {"uid": "free", "name": "Бесплатный", "price": 0},
        {"uid": "standard", "name": "Стандарт", "price": 1000},
    ]
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


@pytest.mark.asyncio
async def test_async_json_handler_read(sample_json):
    result = await AsyncJsonHandler.read(sample_json)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["uid"] == "free"


@pytest.mark.asyncio
async def test_async_json_handler_validate(sample_json):
    assert await AsyncJsonHandler.validate(sample_json) is True

    # empty file
    empty = os.path.join(os.path.dirname(sample_json), "empty.json")
    with open(empty, "w") as f:
        f.write("")
    assert await AsyncJsonHandler.validate(empty) is False

    # invalid json
    bad = os.path.join(os.path.dirname(sample_json), "bad.json")
    with open(bad, "w") as f:
        f.write("not json")
    assert await AsyncJsonHandler.validate(bad) is False


def test_get_plan_by_name():
    plans = [
        {"uid": "free", "name": "Бесплатный"},
        {"uid": "premium", "name": "Премиум"},
    ]
    assert get_plan_by_name(plans, "free")["name"] == "Бесплатный"
    assert get_plan_by_name(plans, "premium")["name"] == "Премиум"
    assert get_plan_by_name(plans, "missing") is None
