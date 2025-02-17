import openai
from openai import AsyncOpenAI

from bot.texts import GPT_TXT
from bot.utils.config import AI_PROMPT, GPT_PLUS_PROMPT


class GPT:
    def __init__(
        self, api_key: str, base_url: str = None
    ):
        openai.api_key = api_key
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.base_url = base_url

        self.name = GPT_TXT

    async def generate(self, model, prompt: str, messages, max_tokens) -> tuple:
        if not messages:
            prompt_2 = AI_PROMPT
            if self.name == GPT_TXT:
                prompt_2 += GPT_PLUS_PROMPT
            print(prompt_2)
            messages = [{"role": "system", "content": prompt_2}]
        messages.append({"role": "user", "content": prompt})

        if not max_tokens:
            response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        else:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=max_tokens,
            )

        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})
        return reply, messages
