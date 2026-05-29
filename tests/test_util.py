from datetime import datetime

from bot.utils.util import format_datetime, escape_markdown_v2


def test_format_datetime():
    dt = datetime(2025, 12, 25)
    assert format_datetime(dt) == "25.12.2025"
    assert format_datetime(None) == "Нет"


def test_escape_markdown_v2():
    text = "Hello_world *bold* [link](url)"
    escaped = escape_markdown_v2(text)
    assert "\\_" in escaped
    assert "\\*" in escaped
    assert "\\[" in escaped
    assert "\\(" in escaped
