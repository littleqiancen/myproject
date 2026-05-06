import json
import asyncio
import logging
from typing import Any
from dataclasses import dataclass, field
import litellm
from app.config import get_settings
from app.utils.exceptions import LLMError

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    parsed_json: Any = None
    usage: dict = field(default_factory=dict)


class LLMClient:
    """基于 LiteLLM 的统一 LLM 调用客户端"""

    def __init__(self, model: str | None = None):
        settings = get_settings()
        self.model = model or settings.DEFAULT_LLM_MODEL
        self.api_base = settings.LLM_API_BASE or None
        self.api_key = self._resolve_api_key()

    @staticmethod
    def _sanitize_api_key(key: str, provider_name: str) -> str:
        """清理并校验 API Key，避免请求头编码错误。"""
        cleaned = (key or "").strip()
        if not cleaned:
            return ""
        if not cleaned.isascii():
            raise LLMError(
                f"{provider_name} API Key 包含非 ASCII 字符，请检查是否粘贴了中文/全角符号或占位文本。"
            )
        return cleaned

    def _resolve_api_key(self) -> str | None:
        """根据全局配置解析 API Key"""
        settings = get_settings()
        openai_key = self._sanitize_api_key(settings.OPENAI_API_KEY, "OpenAI兼容")
        if openai_key:
            return openai_key

        anthropic_key = self._sanitize_api_key(settings.ANTHROPIC_API_KEY, "Anthropic")
        if anthropic_key:
            import os
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            return anthropic_key
        return None

    @staticmethod
    def _resolve_temperature(model: str) -> float:
        """为不同模型选择兼容的温度参数。"""
        normalized = (model or "").split("/")[-1].lower()
        # GPT-5 推理模型通常仅支持 temperature=1（gpt-5-chat 系列除外）
        if normalized.startswith("gpt-5") and not normalized.startswith("gpt-5-chat"):
            return 1.0
        return 0.3

    @staticmethod
    def _resolve_max_tokens(model: str) -> int:
        """根据模型返回合适的 max_tokens，避免超出模型输出上限。"""
        normalized = (model or "").split("/")[-1].lower()
        if normalized in ("deepseek-chat", "deepseek-v3"):
            return 8000
        if normalized in ("deepseek-reasoner", "deepseek-r1"):
            return 16000
        return 16000

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        max_retries: int = 3,
    ) -> LLMResponse:
        """调用 LLM，支持 JSON 模式和指数退避重试"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self._resolve_temperature(self.model),
            "max_tokens": self._resolve_max_tokens(self.model),
        }

        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error = None
        for attempt in range(max_retries):
            try:
                response = await litellm.acompletion(**kwargs)
                content = response.choices[0].message.content

                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

                result = LLMResponse(content=content, usage=usage)

                if json_mode:
                    result.parsed_json = self._parse_json(content)

                return result

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(wait_time)

        raise LLMError(f"LLM调用失败，已重试{max_retries}次: {last_error}")

    @staticmethod
    def _parse_json(content: str) -> Any:
        """解析 JSON，支持 markdown 代码块和截断修复"""
        cleaned = content.strip()
        # 去掉 markdown 代码块包裹
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:])
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # JSON 被截断，尝试修复：补齐缺失的括号
            repaired = cleaned
            # 去掉末尾不完整的值（截断的字符串、数字等）
            # 从最后一个完整的 }, 或 ] 处截断
            last_brace = max(repaired.rfind("},"), repaired.rfind("}]"))
            if last_brace > 0:
                repaired = repaired[:last_brace + 1]
                # 补齐缺失的 ] 和 }
                open_brackets = repaired.count("[") - repaired.count("]")
                open_braces = repaired.count("{") - repaired.count("}")
                repaired += "]" * open_brackets + "}" * open_braces
                logger.warning(f"JSON被截断，已尝试修复（保留到最后完整条目）")
                return json.loads(repaired)
            raise

    @staticmethod
    def get_available_models() -> list[dict]:
        """返回可用模型列表（预设 + 自定义）"""
        preset = [
            {"id": "openai/gpt-4o", "name": "GPT-4o", "provider": "OpenAI"},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI"},
            {"id": "anthropic/claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "provider": "Anthropic"},
            {"id": "anthropic/claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5", "provider": "Anthropic"},
            {"id": "deepseek/deepseek-chat", "name": "DeepSeek Chat", "provider": "DeepSeek"},
        ]
        preset_ids = {m["id"] for m in preset}

        settings = get_settings()
        if settings.DEFAULT_LLM_MODEL and settings.DEFAULT_LLM_MODEL not in preset_ids:
            preset.append({
                "id": settings.DEFAULT_LLM_MODEL,
                "name": settings.DEFAULT_LLM_MODEL,
                "provider": "Custom",
            })

        return preset
