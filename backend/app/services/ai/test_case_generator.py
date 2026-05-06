import asyncio
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.test_point import TestPoint
from app.models.test_case import TestCase
from app.models.generation_batch import GenerationBatch
from app.services.ai.llm_client import LLMClient
from app.services.ai.prompts import (
    TEST_CASE_GENERATION_SYSTEM,
    TEST_CASE_GENERATION_USER,
    RAG_CONTEXT_BLOCK,
)

logger = logging.getLogger(__name__)


async def generate_test_cases(
    db: AsyncSession,
    project_id: str,
    test_point_ids: list[str],
    llm_model: str | None = None,
    knowledge_base_ids: list[str] | None = None,
) -> GenerationBatch:
    """根据测试点生成测试用例（立即返回 batch，后台执行 LLM 调用）"""
    batch = GenerationBatch(
        project_id=project_id,
        batch_type="test_case_generation",
        llm_provider=llm_model,
        status="running",
        started_at=datetime.now(),
    )
    db.add(batch)

    # 标记测试点为"生成中"
    result = await db.execute(
        select(TestPoint).where(TestPoint.id.in_(test_point_ids))
    )
    for tp in result.scalars().all():
        tp.status = "generating"

    await db.commit()
    await db.refresh(batch)

    asyncio.create_task(_run_generation(batch.id, project_id, test_point_ids, llm_model, knowledge_base_ids))

    return batch


async def _run_generation(
    batch_id: str,
    project_id: str,
    test_point_ids: list[str],
    llm_model: str | None,
    knowledge_base_ids: list[str] | None = None,
):
    """后台执行测试用例生成"""
    from app.database import async_session

    async with async_session() as db:
        result = await db.execute(
            select(GenerationBatch).where(GenerationBatch.id == batch_id)
        )
        batch = result.scalar_one()

        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        try:
            result = await db.execute(
                select(TestPoint).where(TestPoint.id.in_(test_point_ids))
            )
            test_points = result.scalars().all()

            if not test_points:
                raise ValueError("未找到指定的测试点")

            client = LLMClient(model=llm_model)

            for point in test_points:
                # 构建 RAG 上下文
                rag_context = ""
                if knowledge_base_ids:
                    from app.services.rag_service import retrieve
                    query = f"{point.title} {point.description}"
                    chunks = await retrieve(knowledge_base_ids, query)
                    if chunks:
                        rag_chunks = "\n\n".join(
                            f"[来源: {c['source_filename']}]\n{c['text']}" for c in chunks
                        )
                        rag_context = RAG_CONTEXT_BLOCK.format(rag_chunks=rag_chunks)

                user_prompt = TEST_CASE_GENERATION_USER.format(
                    title=point.title,
                    description=point.description,
                    priority=point.priority or "P2",
                    category=point.category or "functional",
                    preconditions=point.preconditions or "无",
                    expected_result=point.expected_result or "无",
                    rag_context=rag_context,
                )

                response = await client.chat(
                    system_prompt=TEST_CASE_GENERATION_SYSTEM,
                    user_prompt=user_prompt,
                    json_mode=True,
                )

                for key in total_usage:
                    total_usage[key] += response.usage.get(key, 0)

                cases_data = response.parsed_json
                if isinstance(cases_data, dict) and "test_cases" in cases_data:
                    cases_data = cases_data["test_cases"]
                if not isinstance(cases_data, list):
                    cases_data = [cases_data]

                for case_data in cases_data:
                    steps = case_data.get("steps", [])
                    formatted_steps = []
                    for i, step in enumerate(steps):
                        formatted_steps.append({
                            "step_number": step.get("step_number", i + 1),
                            "action": step.get("action", ""),
                            "expected_result": step.get("expected_result", ""),
                        })

                    # preconditions 可能是 list，需转为字符串
                    preconditions = case_data.get("preconditions", "")
                    if isinstance(preconditions, list):
                        preconditions = "\n".join(preconditions)

                    case = TestCase(
                        project_id=project_id,
                        test_point_id=point.id,
                        title=case_data.get("title", ""),
                        preconditions=preconditions,
                        steps=formatted_steps,
                        priority=case_data.get("priority", point.priority or "P2"),
                        case_type=case_data.get("case_type", "positive"),
                        generation_batch_id=batch.id,
                    )
                    db.add(case)

            batch.status = "completed"
            batch.token_usage = total_usage
            batch.completed_at = datetime.now()

        except Exception as e:
            logger.error(f"测试用例生成失败: {e}")
            batch.status = "failed"
            batch.error_message = str(e)
            batch.completed_at = datetime.now()

        # 恢复测试点状态为 active
        result = await db.execute(
            select(TestPoint).where(TestPoint.id.in_(test_point_ids))
        )
        for tp in result.scalars().all():
            tp.status = "active"

        await db.commit()

        # 发送飞书通知
        if batch.status == "completed":
            try:
                from app.services import notification_service
                await notification_service.send_notification(
                    db, project_id, "test_cases_generated",
                    {"title": "测试用例生成完成", "text": "测试用例生成完成"},
                )
            except Exception as e:
                logger.error(f"发送通知失败: {e}")
