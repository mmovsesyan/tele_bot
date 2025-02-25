from pathlib import Path

import pytz
import yaml

config_dir = Path(__file__).parent.parent.parent.resolve()
config_path = config_dir / "config" / "config.yml"

with open(config_path, "r", encoding='utf-8') as f:
    config = yaml.safe_load(f)

TG_TOKEN = config['TG_TOKEN']

SQLALCHEMY_DB_NAME = config['SQLALCHEMY_DB_NAME']
SQLALCHEMY_IP = config['SQLALCHEMY_IP']
SQLALCHEMY_PORT = config['SQLALCHEMY_PORT']
SQLALCHEMY_USER = config['SQLALCHEMY_USER']
SQLALCHEMY_PASSWORD = config['SQLALCHEMY_PASSWORD']
SQLALCHEMY_URL = f"postgresql+asyncpg://{SQLALCHEMY_USER}:{SQLALCHEMY_PASSWORD}@{SQLALCHEMY_IP}:{SQLALCHEMY_PORT}/{SQLALCHEMY_DB_NAME}"

ADMIN_IDS = list(map(int, str(config['ADMIN_IDS']).split(" ")))

OPENAI_API_KEY = config['OPENAI_API_KEY']
QWEN_API_KEY = config['QWEN_API_KEY']
OPENAI_MODEL = config['OPENAI_MODEL']
QWEN_MODEL = config['QWEN_MODEL']
OPENAI_ADMIN_MODEL = config['OPENAI_ADMIN_MODEL']
OPENAI_ADMIN_TOKEN_LIMIT = config['OPENAI_ADMIN_TOKEN_LIMIT']
BOT_USERNAME = ''

TIMEZONE = pytz.timezone(config['TIMEZONE'])

REDIS_HOST = config['REDIS_HOST']
REDIS_DB = config['REDIS_DB']

CKASSA_BASE_URL = config['CKASSA_BASE_URL']
ApiLoginAuthorization = config['ApiLoginAuthorization']
ApiAuthorization = config['ApiAuthorization']
servCode = config['servCode']
CKASSA_WEBHOOKS_URL = config['CKASSA_WEBHOOKS_URL']
CKASSA_WEBHOOKS_PORT = config['CKASSA_WEBHOOKS_PORT']
CKASSA_MAIN_PROPERTY = config['CKASSA_MAIN_PROPERTY']

QWEN_IMAGE_MODEL = config['QWEN_IMAGE_MODEL']

GEN_VIDEO_DURATION = config['GEN_VIDEO_DURATION']
GEN_VIDEO_ASPECT_RATIO = config['GEN_VIDEO_ASPECT_RATIO']
GEN_VIDEO_API_KEY = config['GEN_VIDEO_API_KEY']
BACKUP_DIR = 'backups'

AI_PROMPT = "Отвечай строго на русском языке!Тебе нельзя отвечать на китайском языке!Все ответы выдавай в читаемом виде!"
GPT_PLUS_PROMPT = "\n\nЕсли спросят, то ты - модель gpt4o или gpt o3-high. В зависимости от сложности вашего ответа"
