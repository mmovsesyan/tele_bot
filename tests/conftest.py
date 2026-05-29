import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure config directory exists with a dummy config.yml for imports
config_dir = Path(project_root) / "config"
config_dir.mkdir(exist_ok=True)
config_path = config_dir / "config.yml"

if not config_path.exists():
    config_path.write_text("""
TG_TOKEN: test_token
SQLALCHEMY_DB_NAME: testdb
SQLALCHEMY_IP: localhost
SQLALCHEMY_PORT: 5432
SQLALCHEMY_USER: test
SQLALCHEMY_PASSWORD: test
ADMIN_IDS: 123
OPENAI_API_KEY: test
OPENAI_MODEL: test
OPENAI_ADMIN_MODEL: test
OPENAI_ADMIN_TOKEN_LIMIT: 1000
QWEN_API_KEY: test
QWEN_MODEL: test
ANTHROPIC_API_KEY: test
ANTHROPIC_MODEL: test
OLLAMA_API_KEY: test
OLLAMA_BASE_URL: https://api.ollama.com/v1/
OLLAMA_GPT_MODEL: test
OLLAMA_QWEN_MODEL: test
OLLAMA_CLAUDE_MODEL: test
OLLAMA_ADMIN_MODEL: test
TIMEZONE: Europe/Moscow
REDIS_HOST: 6379
REDIS_DB: 0
""", encoding="utf-8")

# Copy plans.json for tests
plans_src = Path(project_root) / "config_example" / "plans.json"
plans_dst = config_dir / "plans.json"
if plans_src.exists() and not plans_dst.exists():
    plans_dst.write_text(plans_src.read_text(), encoding="utf-8")
