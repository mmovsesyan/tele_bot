from bot.ai.gpt import GPT
from bot.texts import QWEN_TXT


class Qwen(GPT):
    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key, base_url)
        self.name = QWEN_TXT
