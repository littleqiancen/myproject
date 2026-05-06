from pydantic import BaseModel
from datetime import datetime


# AI操作相关的请求/响应模型

class ExtractTestPointsRequest(BaseModel):
    document_ids: list[str]
    llm_model: str | None = None
    knowledge_base_ids: list[str] | None = None


class RegenerateTestPointsRequest(BaseModel):
    document_ids: list[str]
    existing_point_ids: list[str] | None = None
    feedback: str | None = None
    llm_model: str | None = None
    knowledge_base_ids: list[str] | None = None


class GenerateTestCasesRequest(BaseModel):
    test_point_ids: list[str]
    llm_model: str | None = None
    knowledge_base_ids: list[str] | None = None


class BatchStatusResponse(BaseModel):
    id: str
    batch_type: str
    status: str
    error_message: str | None = None
    token_usage: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class LLMModelInfo(BaseModel):
    id: str
    name: str
    provider: str


class SettingsResponse(BaseModel):
    default_llm_model: str
    llm_api_base: str
    feishu_webhook_url: str
    feishu_webhook_secret: str
    openai_api_key_set: bool
    anthropic_api_key_set: bool
    openai_api_key: str = ""
    anthropic_api_key: str = ""


class SettingsUpdate(BaseModel):
    default_llm_model: str | None = None
    llm_api_base: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    feishu_webhook_url: str | None = None
    feishu_webhook_secret: str | None = None
