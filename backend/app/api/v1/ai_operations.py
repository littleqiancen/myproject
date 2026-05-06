from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import (
    ExtractTestPointsRequest, RegenerateTestPointsRequest,
    GenerateTestCasesRequest, BatchStatusResponse,
    LLMModelInfo, SettingsResponse, SettingsUpdate,
)
from app.schemas.notification import TestNotificationRequest
from app.services.ai.test_point_extractor import extract_test_points, regenerate_test_points
from app.services.ai.test_case_generator import generate_test_cases
from app.services.ai.llm_client import LLMClient
from app.services import notification_service
from app.models.generation_batch import GenerationBatch
from app.config import get_settings, save_settings_to_file
from app.integrations.feishu import test_webhook
from app.utils.exceptions import BadRequestError
from sqlalchemy import select

router = APIRouter(tags=["AI操作"])


@router.post("/projects/{project_id}/ai/extract-test-points", response_model=BatchStatusResponse)
async def api_extract_test_points(
    project_id: str,
    data: ExtractTestPointsRequest,
    db: AsyncSession = Depends(get_db),
):
    batch = await extract_test_points(
        db, project_id, data.document_ids, data.llm_model, data.knowledge_base_ids
    )
    return BatchStatusResponse.model_validate(batch)


@router.post("/projects/{project_id}/ai/regenerate-test-points", response_model=BatchStatusResponse)
async def api_regenerate_test_points(
    project_id: str,
    data: RegenerateTestPointsRequest,
    db: AsyncSession = Depends(get_db),
):
    batch = await regenerate_test_points(
        db, project_id, data.document_ids,
        data.existing_point_ids, data.feedback, data.llm_model, data.knowledge_base_ids,
    )
    return BatchStatusResponse.model_validate(batch)


@router.post("/projects/{project_id}/ai/generate-test-cases", response_model=BatchStatusResponse)
async def api_generate_test_cases(
    project_id: str,
    data: GenerateTestCasesRequest,
    db: AsyncSession = Depends(get_db),
):
    batch = await generate_test_cases(
        db, project_id, data.test_point_ids, data.llm_model, data.knowledge_base_ids,
    )
    return BatchStatusResponse.model_validate(batch)


@router.get("/projects/{project_id}/ai/running-batches", response_model=list[BatchStatusResponse])
async def get_running_batches(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取项目中正在运行的批次"""
    result = await db.execute(
        select(GenerationBatch).where(
            GenerationBatch.project_id == project_id,
            GenerationBatch.status == "running",
        )
    )
    batches = result.scalars().all()
    return [BatchStatusResponse.model_validate(b) for b in batches]


@router.get("/ai/batches/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GenerationBatch).where(GenerationBatch.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        from app.utils.exceptions import NotFoundError
        raise NotFoundError("批次")
    return BatchStatusResponse.model_validate(batch)


@router.get("/ai/models", response_model=list[LLMModelInfo])
async def get_available_models():
    models = LLMClient.get_available_models()
    return [LLMModelInfo(**m) for m in models]


# ==================== 通知 ====================

@router.get("/projects/{project_id}/notifications")
async def list_notifications(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    items, total = await notification_service.get_notifications(db, project_id)
    return {"items": items, "total": total}


@router.post("/notifications/test")
async def test_notification(data: TestNotificationRequest):
    await test_webhook(data.webhook_url, data.webhook_secret)
    return {"status": "ok", "message": "通知发送成功"}


# ==================== 设置 ====================

def _mask_key(key: str) -> str:
    """对 API Key 进行脱敏：保留前6位和后4位"""
    if not key or len(key) <= 10:
        return key
    return key[:6] + "*" * (len(key) - 10) + key[-4:]


def _normalize_api_key(key: str, provider_name: str) -> str:
    """清理并校验 API Key，避免保存非法值。"""
    cleaned = key.strip()
    if not cleaned:
        return ""
    if not cleaned.isascii():
        raise BadRequestError(
            f"{provider_name} API Key 包含非 ASCII 字符，请检查是否粘贴了中文/全角符号或占位文本"
        )
    return cleaned


def _build_settings_response(settings) -> SettingsResponse:
    return SettingsResponse(
        default_llm_model=settings.DEFAULT_LLM_MODEL,
        llm_api_base=settings.LLM_API_BASE,
        feishu_webhook_url=settings.FEISHU_WEBHOOK_URL,
        feishu_webhook_secret=settings.FEISHU_WEBHOOK_SECRET,
        openai_api_key_set=bool(settings.OPENAI_API_KEY),
        anthropic_api_key_set=bool(settings.ANTHROPIC_API_KEY),
        openai_api_key=_mask_key(settings.OPENAI_API_KEY),
        anthropic_api_key=_mask_key(settings.ANTHROPIC_API_KEY),
    )


@router.get("/settings", response_model=SettingsResponse)
async def get_app_settings():
    settings = get_settings()
    return _build_settings_response(settings)


@router.put("/settings", response_model=SettingsResponse)
async def update_app_settings(data: SettingsUpdate):
    import os

    settings = get_settings()

    if data.default_llm_model is not None:
        settings.DEFAULT_LLM_MODEL = data.default_llm_model
        os.environ["DEFAULT_LLM_MODEL"] = data.default_llm_model
    if data.llm_api_base is not None:
        settings.LLM_API_BASE = data.llm_api_base
        os.environ["LLM_API_BASE"] = data.llm_api_base
    if data.openai_api_key is not None and "*" not in data.openai_api_key:
        # 只有非脱敏值才更新（包含 * 的是前端回传的脱敏值，忽略）
        normalized_openai_key = _normalize_api_key(data.openai_api_key, "OpenAI兼容")
        settings.OPENAI_API_KEY = normalized_openai_key
        if normalized_openai_key:
            os.environ["OPENAI_API_KEY"] = normalized_openai_key
        else:
            os.environ.pop("OPENAI_API_KEY", None)
    if data.anthropic_api_key is not None and "*" not in data.anthropic_api_key:
        normalized_anthropic_key = _normalize_api_key(data.anthropic_api_key, "Anthropic")
        settings.ANTHROPIC_API_KEY = normalized_anthropic_key
        if normalized_anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = normalized_anthropic_key
        else:
            os.environ.pop("ANTHROPIC_API_KEY", None)
    if data.feishu_webhook_url is not None:
        settings.FEISHU_WEBHOOK_URL = data.feishu_webhook_url
        os.environ["FEISHU_WEBHOOK_URL"] = data.feishu_webhook_url
    if data.feishu_webhook_secret is not None:
        settings.FEISHU_WEBHOOK_SECRET = data.feishu_webhook_secret
        os.environ["FEISHU_WEBHOOK_SECRET"] = data.feishu_webhook_secret

    # 持久化到 settings.json
    save_settings_to_file(settings)

    # 清除缓存使新设置从环境变量重新加载
    get_settings.cache_clear()

    return _build_settings_response(settings)
