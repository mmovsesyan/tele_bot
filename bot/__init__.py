from bot.ai.gpt import GPT
from bot.ai.qwen import Qwen
from bot.ai.veo import VeoAPI
from bot.payments.ckassa.app import CKassa
from bot.utils.config import OPENAI_API_KEY, OPENAI_MODEL, QWEN_API_KEY, QWEN_MODEL, CKASSA_BASE_URL, \
    CKASSA_WEBHOOKS_URL, GEN_VIDEO_API_KEY
from bot.utils.converter import CurrencyConverter
from bot.utils.json_worker import AsyncJsonHandler

AI = {
    'gpt': GPT(OPENAI_API_KEY),
    'qwen': Qwen(QWEN_API_KEY, "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
}

ckassa = CKassa(CKASSA_BASE_URL, CKASSA_WEBHOOKS_URL)

veoapi = VeoAPI(GEN_VIDEO_API_KEY)

json_worker = AsyncJsonHandler()

converter = CurrencyConverter