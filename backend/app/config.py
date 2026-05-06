import json
import os
import logging
from pydantic_settings import BaseSettings
from functools import lru_cache

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
logger = logging.getLogger(__name__)

# 可通过 UI 持久化的字段
_PERSISTABLE_KEYS = {
    "DEFAULT_LLM_MODEL", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "LLM_API_BASE", "FEISHU_WEBHOOK_URL", "FEISHU_WEBHOOK_SECRET",
}


class Settings(BaseSettings):
    # Database
    DATABASE_PATH: str = "casegen.db"

    # LLM
    DEFAULT_LLM_MODEL: str = "openai/gpt-4o"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_API_BASE: str = ""

    # Feishu
    FEISHU_WEBHOOK_URL: str = ""
    FEISHU_WEBHOOK_SECRET: str = ""

    # RAG / Knowledge Base
    CHROMADB_PATH: str = "chromadb_data"
    EMBEDDING_PROVIDER: str = "local"  # "local" (sentence-transformers) or "openai"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # or "text-embedding-3-small" for openai
    CHUNK_SIZE: int = 512  # approximate tokens per chunk
    CHUNK_OVERLAP: int = 64  # overlap tokens between chunks
    RAG_TOP_K: int = 5  # number of chunks to retrieve

    # App
    BACKEND_PORT: int = 8000
    MAX_UPLOAD_SIZE_MB: int = 50
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.DATABASE_PATH}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def _load_persisted() -> dict:
    """从 settings.json 加载已保存的配置"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings_to_file(settings: Settings) -> None:
    """将可持久化的设置写入 settings.json"""
    data = {}
    for key in _PERSISTABLE_KEYS:
        val = getattr(settings, key, "")
        if val:  # 只保存非空值
            data[key] = val
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _is_invalid_persisted_api_key(key: str, val: str) -> bool:
    """判断持久化 API Key 是否为明显非法值（如中文占位文本）。"""
    if key not in {"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}:
        return False
    if not isinstance(val, str):
        return True
    cleaned = val.strip()
    if not cleaned:
        return True
    # HTTP Header 要求 ASCII，非 ASCII 会导致编码异常
    return not cleaned.isascii()


@lru_cache
def get_settings() -> Settings:
    # 先让 pydantic-settings 从 .env / 环境变量加载
    s = Settings()
    # 再用 settings.json 中的值覆盖（UI 配置优先于环境变量）
    persisted = _load_persisted()
    for key, val in persisted.items():
        if key in _PERSISTABLE_KEYS and val:
            if _is_invalid_persisted_api_key(key, val):
                logger.warning(f"忽略无效的持久化配置 {key}（包含非 ASCII 字符）")
                continue
            setattr(s, key, val)
            os.environ[key] = val
    return s
