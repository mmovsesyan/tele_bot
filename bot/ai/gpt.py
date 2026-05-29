import base64

import openai
from openai import AsyncOpenAI

from bot.texts import GPT_TXT, QWEN_TXT
from bot.utils.config import AI_PROMPT, GPT_PLUS_PROMPT


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


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

    async def generate(self, model, prompt: str, messages, max_tokens, photo_path) -> tuple:
        if not messages:
            prompt_2 = AI_PROMPT
            if self.name == GPT_TXT:
                prompt_2 += GPT_PLUS_PROMPT
            messages = [{"role": "system", "content": prompt_2}]
        if photo_path:
            base64_image = encode_image(photo_path)
            messages.append(
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                    {"type": "text", "text": prompt},
                ]}
            )
        else:
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


    async def get_text(self, audio_path):
        with open(audio_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            return transcript.text

