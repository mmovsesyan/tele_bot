from pathlib import Path

import pytz
import yaml

config_dir = Path(__file__).parent.parent.parent.resolve()
config_path = config_dir / "config" / "config.yml"

with open(config_path, "r") as f:
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

BOT_USERNAME = ''

TIMEZONE = pytz.timezone(config['TIMEZONE'])

REDIS_HOST = config['REDIS_HOST']
REDIS_DB = config['REDIS_DB']

CKASSA_BASE_URL = config['CKASSA_BASE_URL']
CKASSA_SHOP_TOKEN = config['CKASSA_SHOP_TOKEN']
CKASSA_SEC_KEY = config['CKASSA_SEC_KEY']
CKASSA_SERVICE_CODE = config['CKASSA_SERVICE_CODE']
CKASSA_WEBHOOKS_URL = config['CKASSA_WEBHOOKS_URL']
CKASSA_WEBHOOKS_PORT = config['CKASSA_WEBHOOKS_PORT']

BACKUP_DIR = 'backups'

AI_PROMPT = "Отвечай строго на русском языке!Тебе нельзя отвечать на китайском языке!"