from bot.ai.gpt import GPT
from bot.texts import ANTHROPIC_TXT


class AnthropicAI(GPT):
    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key, base_url)
        self.name = ANTHROPIC_TXT
