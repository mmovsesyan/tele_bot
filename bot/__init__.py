from bot.ai.anthropic_ai import AnthropicAI
from bot.ai.gpt import GPT
from bot.ai.qwen import Qwen
from bot.ai.veo import VeoAPI
from bot.utils.config import GEN_VIDEO_API_KEY, OPENAI_API_KEY, OLLAMA_API_KEY, OLLAMA_BASE_URL
from bot.utils.converter import CurrencyConverter
from bot.utils.json_worker import AsyncJsonHandler

AI = {
    'gpt': GPT(OLLAMA_API_KEY, OLLAMA_BASE_URL),
    'qwen': Qwen(OLLAMA_API_KEY, OLLAMA_BASE_URL),
    'claude': AnthropicAI(OLLAMA_API_KEY, OLLAMA_BASE_URL)
}

image_ai = GPT(OPENAI_API_KEY)

veoapi = VeoAPI(GEN_VIDEO_API_KEY)

json_worker = AsyncJsonHandler()

converter = CurrencyConverter