from bot.ai.gpt import GPT
from bot.texts import QWEN_TXT


class Qwen(GPT):
    def __init__(self, api_key: str, model: str, base_url: str):
        super().__init__(api_key, model, base_url)
        self.name = QWEN_TXT
