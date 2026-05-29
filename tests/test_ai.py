import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.ai.gpt import GPT, encode_image


@pytest.mark.asyncio
async def test_gpt_generate():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Привет! Это тестовый ответ."
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("bot.ai.gpt.AsyncOpenAI", return_value=mock_client):
        gpt = GPT("fake-api-key", "https://fake.ollama.com/v1")
        reply, messages = await gpt.generate(
            model="gpt-oss:20b-cloud",
            prompt="Скажи привет",
            messages=[],
            max_tokens=None,
            photo_path=None,
        )

    assert reply == "Привет! Это тестовый ответ."
    assert len(messages) == 3  # system + user prompt + assistant reply
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"] == "Привет! Это тестовый ответ."


@pytest.mark.asyncio
async def test_gpt_generate_with_history():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Ответ с историей"
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("bot.ai.gpt.AsyncOpenAI", return_value=mock_client):
        gpt = GPT("fake-api-key")
        history = [
            {"role": "user", "content": "Вопрос 1"},
            {"role": "assistant", "content": "Ответ 1"},
        ]
        reply, messages = await gpt.generate(
            model="gpt-oss:20b-cloud",
            prompt="Вопрос 2",
            messages=history,
            max_tokens=None,
            photo_path=None,
        )

    assert reply == "Ответ с историей"
    assert len(messages) == 4


@pytest.mark.asyncio
async def test_gpt_gen_image():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock()]
    mock_response.data[0].url = "https://example.com/image.png"
    mock_client.images.generate = AsyncMock(return_value=mock_response)

    with patch("bot.ai.gpt.AsyncOpenAI", return_value=mock_client):
        gpt = GPT("fake-api-key")
        url = await gpt.gen_image("кот в шляпе")

    assert url == "https://example.com/image.png"


def test_encode_image(tmp_path):
    img_path = tmp_path / "test.jpg"
    img_path.write_bytes(b"fake_image_data")
    result = encode_image(str(img_path))
    assert isinstance(result, str)
    assert result == "ZmFrZV9pbWFnZV9kYXRh"
