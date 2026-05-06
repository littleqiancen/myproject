import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseDocument
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseDocumentResponse,
)
from app.utils.file_utils import save_upload_file
from app.utils.exceptions import NotFoundError, BadRequestError
from app.services.ai.document_parser import parse_document
from app.services import rag_service

logger = logging.getLogger(__name__)

ALLOWED_KB_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}


async def create_knowledge_base(
    db: AsyncSession, project_id: str, data: KnowledgeBaseCreate
) -> KnowledgeBaseResponse:
    kb = KnowledgeBase(
        project_id=project_id,
        name=data.name,
        description=data.description,
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return KnowledgeBaseResponse.model_validate(kb)


async def list_knowledge_bases(
    db: AsyncSession, project_id: str
) -> tuple[list[KnowledgeBaseResponse], int]:
    count_result = await db.execute(
        select(func.count(KnowledgeBase.id)).where(KnowledgeBase.project_id == project_id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.project_id == project_id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    kbs = result.scalars().all()
    return [KnowledgeBaseResponse.model_validate(kb) for kb in kbs], total


async def get_knowledge_base(db: AsyncSession, kb_id: str) -> KnowledgeBaseResponse:
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise NotFoundError("知识库")
    return KnowledgeBaseResponse.model_validate(kb)


async def update_knowledge_base(
    db: AsyncSession, kb_id: str, data: KnowledgeBaseUpdate
) -> KnowledgeBaseResponse:
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise NotFoundError("知识库")
    if data.name is not None:
        kb.name = data.name
    if data.description is not None:
        kb.description = data.description
    await db.commit()
    await db.refresh(kb)
    return KnowledgeBaseResponse.model_validate(kb)


async def delete_knowledge_base(db: AsyncSession, kb_id: str) -> None:
    result = await db.execute(
        select(KnowledgeBase)
        .options(selectinload(KnowledgeBase.documents))
        .where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    if not kb:
        raise NotFoundError("知识库")
    # 删除 ChromaDB collection
    await rag_service.delete_collection(kb_id)
    # 删除磁盘文件
    for doc in kb.documents:
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    await db.delete(kb)
    await db.commit()


async def upload_kb_documents(
    db: AsyncSession, kb_id: str, files: list[UploadFile]
) -> list[KnowledgeBaseDocumentResponse]:
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise NotFoundError("知识库")

    results = []
    for file in files:
        ext = os.path.splitext(file.filename.lower())[1]
        if ext not in ALLOWED_KB_EXTENSIONS:
            raise BadRequestError(f"不支持的文件类型: {ext}，仅支持 PDF、DOCX、MD、TXT")
        file_type = ext[1:]

        file_path, file_size = await save_upload_file(file, f"kb_{kb_id}")

        kb_doc = KnowledgeBaseDocument(
            knowledge_base_id=kb_id,
            filename=file.filename,
            file_type=file_type,
            file_path=file_path,
            file_size=file_size,
            status="pending",
        )
        db.add(kb_doc)
        await db.commit()
        await db.refresh(kb_doc)

        # 启动后台处理
        asyncio.create_task(_process_kb_document(kb_id, kb_doc.id))

        results.append(KnowledgeBaseDocumentResponse.model_validate(kb_doc))

    return results


async def _process_kb_document(kb_id: str, kb_doc_id: str) -> None:
    """后台任务：解析文档 → 分块 → embedding → 存入 ChromaDB"""
    from app.database import async_session

    async with async_session() as db:
        result = await db.execute(
            select(KnowledgeBaseDocument).where(KnowledgeBaseDocument.id == kb_doc_id)
        )
        kb_doc = result.scalar_one()

        try:
            kb_doc.status = "processing"
            await db.commit()

            # 解析文档
            if kb_doc.file_type == "txt":
                with open(kb_doc.file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            else:
                parse_result = await parse_document(kb_doc.file_path, kb_doc.file_type)
                text = parse_result.markdown or parse_result.raw_text

            # 索引到 ChromaDB
            chunk_count = await rag_service.index_document(
                kb_id, kb_doc_id, kb_doc.filename, text
            )

            kb_doc.chunk_count = chunk_count
            kb_doc.status = "completed"
            await db.commit()

            # 更新知识库聚合计数
            await _update_kb_counts(db, kb_id)

        except Exception as e:
            logger.error(f"知识库文档处理失败: {e}")
            kb_doc.status = "failed"
            kb_doc.error_message = str(e)
            await db.commit()


async def _update_kb_counts(db: AsyncSession, kb_id: str) -> None:
    """更新知识库的 document_count 和 chunk_count"""
    doc_count = (await db.execute(
        select(func.count(KnowledgeBaseDocument.id))
        .where(KnowledgeBaseDocument.knowledge_base_id == kb_id)
    )).scalar()

    chunk_sum = (await db.execute(
        select(func.coalesce(func.sum(KnowledgeBaseDocument.chunk_count), 0))
        .where(KnowledgeBaseDocument.knowledge_base_id == kb_id)
    )).scalar()

    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one()
    kb.document_count = doc_count
    kb.chunk_count = chunk_sum
    await db.commit()


async def delete_kb_document(db: AsyncSession, kb_doc_id: str) -> None:
    result = await db.execute(
        select(KnowledgeBaseDocument).where(KnowledgeBaseDocument.id == kb_doc_id)
    )
    kb_doc = result.scalar_one_or_none()
    if not kb_doc:
        raise NotFoundError("知识库文档")

    kb_id = kb_doc.knowledge_base_id

    # 删除 ChromaDB 中的分块
    await rag_service.delete_document_chunks(kb_id, kb_doc_id)

    # 删除文件
    if kb_doc.file_path and os.path.exists(kb_doc.file_path):
        os.remove(kb_doc.file_path)

    await db.delete(kb_doc)
    await db.commit()

    # 更新计数
    await _update_kb_counts(db, kb_id)


async def list_kb_documents(
    db: AsyncSession, kb_id: str
) -> tuple[list[KnowledgeBaseDocumentResponse], int]:
    count_result = await db.execute(
        select(func.count(KnowledgeBaseDocument.id))
        .where(KnowledgeBaseDocument.knowledge_base_id == kb_id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(KnowledgeBaseDocument)
        .where(KnowledgeBaseDocument.knowledge_base_id == kb_id)
        .order_by(KnowledgeBaseDocument.created_at.desc())
    )
    docs = result.scalars().all()
    return [KnowledgeBaseDocumentResponse.model_validate(d) for d in docs], total
