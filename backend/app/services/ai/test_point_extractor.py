import json
import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document
from app.models.test_point import TestPoint
from app.models.generation_batch import GenerationBatch
from app.services.ai.llm_client import LLMClient
from app.services.ai.prompts import (
    TEST_POINT_EXTRACTION_SYSTEM,
    TEST_POINT_EXTRACTION_USER,
    TEST_POINT_REGENERATION_USER,
    RAG_CONTEXT_BLOCK,
)

logger = logging.getLogger(__name__)


def _extract_points_list(data) -> list[dict]:
    """从 LLM 返回的各种 JSON 格式中提取测试点列表"""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 尝试常见的 key: test_points, testPoints, points, data, results 等
        for key in ("test_points", "testPoints", "points", "data", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # 如果 dict 中只有一个 key 且值是 list，取它
        values = list(data.values())
        if len(values) == 1 and isinstance(values[0], list):
            return values[0]
        # dict 本身可能就是单个测试点
        if "title" in data:
            return [data]
    return [data]


async def extract_test_points(
    db: AsyncSession,
    project_id: str,
    document_ids: list[str],
    llm_model: str | None = None,
    knowledge_base_ids: list[str] | None = None,
) -> GenerationBatch:
    """从文档中提取测试点（立即返回 batch，后台执行 LLM 调用）"""
    # 创建批次记录
    batch = GenerationBatch(
        project_id=project_id,
        batch_type="test_point_extraction",
        document_ids=document_ids,
        llm_provider=llm_model,
        status="running",
        started_at=datetime.now(),
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)

    # 后台执行 LLM 调用
    asyncio.create_task(_run_extraction(batch.id, project_id, document_ids, llm_model, knowledge_base_ids))

    return batch


async def _run_extraction(
    batch_id: str,
    project_id: str,
    document_ids: list[str],
    llm_model: str | None,
    knowledge_base_ids: list[str] | None = None,
):
    """后台执行测试点提取"""
    from app.database import async_session

    async with async_session() as db:
        result = await db.execute(
            select(GenerationBatch).where(GenerationBatch.id == batch_id)
        )
        batch = result.scalar_one()

        try:
            document_content = await _get_documents_content(db, document_ids)

            # 构建 RAG 上下文
            rag_context = ""
            if knowledge_base_ids:
                from app.services.rag_service import retrieve
                chunks = await retrieve(knowledge_base_ids, document_content[:2000])
                if chunks:
                    rag_chunks = "\n\n".join(
                        f"[来源: {c['source_filename']}]\n{c['text']}" for c in chunks
                    )
                    rag_context = RAG_CONTEXT_BLOCK.format(rag_chunks=rag_chunks)

            client = LLMClient(model=llm_model)
            response = await client.chat(
                system_prompt=TEST_POINT_EXTRACTION_SYSTEM,
                user_prompt=TEST_POINT_EXTRACTION_USER.format(
                    document_content=document_content,
                    rag_context=rag_context,
                ),
                json_mode=True,
            )

            points_data = response.parsed_json
            logger.info(f"LLM 返回 JSON 类型: {type(points_data).__name__}, 内容预览: {str(points_data)[:500]}")
            points_data = _extract_points_list(points_data)

            for i, point_data in enumerate(points_data):
                if not isinstance(point_data, dict):
                    logger.warning(f"跳过非字典类型的测试点: {point_data}")
                    continue
                title = point_data.get("title", "").strip()
                description = point_data.get("description", "").strip()
                if not title and not description:
                    logger.warning(f"跳过空测试点: {point_data}")
                    continue
                point = TestPoint(
                    project_id=project_id,
                    document_id=document_ids[0] if document_ids else None,
                    title=title,
                    description=description,
                    priority=point_data.get("priority", "P2"),
                    category=point_data.get("category", "functional"),
                    preconditions=point_data.get("preconditions", ""),
                    expected_result=point_data.get("expected_result", ""),
                    source_context=point_data.get("source_context", ""),
                    generation_batch_id=batch.id,
                    sort_order=i,
                )
                db.add(point)

            batch.status = "completed"
            batch.token_usage = response.usage
            batch.completed_at = datetime.now()

        except Exception as e:
            logger.error(f"测试点提取失败: {e}")
            batch.status = "failed"
            batch.error_message = str(e)
            batch.completed_at = datetime.now()

        await db.commit()

        # 发送飞书通知
        if batch.status == "completed":
            await _send_completion_notification(db, project_id, "test_points_generated", "测试点提取完成")


async def regenerate_test_points(
    db: AsyncSession,
    project_id: str,
    document_ids: list[str],
    existing_point_ids: list[str] | None = None,
    feedback: str | None = None,
    llm_model: str | None = None,
    knowledge_base_ids: list[str] | None = None,
) -> GenerationBatch:
    """重新生成测试点（立即返回 batch，后台执行 LLM 调用）"""
    batch = GenerationBatch(
        project_id=project_id,
        batch_type="test_point_extraction",
        document_ids=document_ids,
        llm_provider=llm_model,
        status="running",
        started_at=datetime.now(),
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)

    # 预先读取已有测试点文本（在当前 session 中）
    existing_points_text = ""
    if existing_point_ids:
        result = await db.execute(
            select(TestPoint).where(TestPoint.id.in_(existing_point_ids))
        )
        existing = result.scalars().all()
        existing_points_text = json.dumps(
            [{"title": p.title, "description": p.description, "priority": p.priority}
             for p in existing],
            ensure_ascii=False, indent=2
        )

    asyncio.create_task(_run_regeneration(
        batch.id, project_id, document_ids, existing_points_text, feedback, llm_model, knowledge_base_ids
    ))

    return batch


async def _run_regeneration(
    batch_id: str,
    project_id: str,
    document_ids: list[str],
    existing_points_text: str,
    feedback: str | None,
    llm_model: str | None,
    knowledge_base_ids: list[str] | None = None,
):
    """后台执行测试点重新生成"""
    from app.database import async_session

    async with async_session() as db:
        result = await db.execute(
            select(GenerationBatch).where(GenerationBatch.id == batch_id)
        )
        batch = result.scalar_one()

        try:
            document_content = await _get_documents_content(db, document_ids)

            # 构建 RAG 上下文
            rag_context = ""
            if knowledge_base_ids:
                from app.services.rag_service import retrieve
                chunks = await retrieve(knowledge_base_ids, document_content[:2000])
                if chunks:
                    rag_chunks = "\n\n".join(
                        f"[来源: {c['source_filename']}]\n{c['text']}" for c in chunks
                    )
                    rag_context = RAG_CONTEXT_BLOCK.format(rag_chunks=rag_chunks)

            client = LLMClient(model=llm_model)
            response = await client.chat(
                system_prompt=TEST_POINT_EXTRACTION_SYSTEM,
                user_prompt=TEST_POINT_REGENERATION_USER.format(
                    document_content=document_content,
                    rag_context=rag_context,
                    existing_points=existing_points_text or "无",
                    feedback=feedback or "无",
                ),
                json_mode=True,
            )

            points_data = response.parsed_json
            logger.info(f"LLM 返回 JSON 类型: {type(points_data).__name__}, 内容预览: {str(points_data)[:500]}")
            points_data = _extract_points_list(points_data)

            for i, point_data in enumerate(points_data):
                if not isinstance(point_data, dict):
                    logger.warning(f"跳过非字典类型的测试点: {point_data}")
                    continue
                title = point_data.get("title", "").strip()
                description = point_data.get("description", "").strip()
                if not title and not description:
                    logger.warning(f"跳过空测试点: {point_data}")
                    continue
                point = TestPoint(
                    project_id=project_id,
                    document_id=document_ids[0] if document_ids else None,
                    title=title,
                    description=description,
                    priority=point_data.get("priority", "P2"),
                    category=point_data.get("category", "functional"),
                    preconditions=point_data.get("preconditions", ""),
                    expected_result=point_data.get("expected_result", ""),
                    source_context=point_data.get("source_context", ""),
                    generation_batch_id=batch.id,
                    sort_order=i,
                )
                db.add(point)

            batch.status = "completed"
            batch.token_usage = response.usage
            batch.completed_at = datetime.now()

        except Exception as e:
            logger.error(f"测试点重新生成失败: {e}")
            batch.status = "failed"
            batch.error_message = str(e)
            batch.completed_at = datetime.now()

        await db.commit()

        if batch.status == "completed":
            await _send_completion_notification(db, project_id, "test_points_generated", "测试点重新生成完成")


async def _send_completion_notification(
    db: AsyncSession, project_id: str, event_type: str, title: str
):
    """AI 任务完成后发送飞书通知"""
    try:
        from app.services import notification_service
        await notification_service.send_notification(
            db, project_id, event_type, {"title": title, "text": title}
        )
    except Exception as e:
        logger.error(f"发送通知失败: {e}")


async def _get_documents_content(db: AsyncSession, document_ids: list[str]) -> str:
    """获取并合并多个文档的Markdown内容"""
    result = await db.execute(
        select(Document).where(Document.id.in_(document_ids))
    )
    docs = result.scalars().all()

    parts = []
    for doc in docs:
        content = doc.parsed_markdown or doc.raw_text or ""
        if content:
            parts.append(f"## 文档: {doc.filename}\n\n{content}")

    return "\n\n---\n\n".join(parts)
