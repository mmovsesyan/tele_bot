import openai
from openai import AsyncOpenAI

from bot.texts import GPT_TXT
from bot.utils.config import AI_PROMPT


class GPT:
    def __init__(
        self, api_key: str, model: str, base_url: str = None
    ):
        openai.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.base_url = base_url

        self.name = GPT_TXT

    async def generate(self, prompt: str, messages, max_tokens) -> tuple:
        if not messages:
            messages = [{"role": "system", "content": AI_PROMPT}]
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=max_tokens,
        )

        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})
        return reply, messages
