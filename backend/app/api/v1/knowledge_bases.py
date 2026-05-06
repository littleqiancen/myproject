from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseDocumentResponse,
    KnowledgeBaseDocumentListResponse,
)
from app.services import knowledge_base_service

router = APIRouter(tags=["知识库管理"])


@router.post("/projects/{project_id}/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    project_id: str,
    data: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
):
    return await knowledge_base_service.create_knowledge_base(db, project_id, data)


@router.get("/projects/{project_id}/knowledge-bases", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    items, total = await knowledge_base_service.list_knowledge_bases(db, project_id)
    return KnowledgeBaseListResponse(items=items, total=total)


@router.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await knowledge_base_service.get_knowledge_base(db, kb_id)


@router.put("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    data: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await knowledge_base_service.update_knowledge_base(db, kb_id, data)


@router.delete("/knowledge-bases/{kb_id}", status_code=204)
async def delete_knowledge_base(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
):
    await knowledge_base_service.delete_knowledge_base(db, kb_id)


@router.post(
    "/knowledge-bases/{kb_id}/documents/upload",
    response_model=list[KnowledgeBaseDocumentResponse],
)
async def upload_kb_documents(
    kb_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await knowledge_base_service.upload_kb_documents(db, kb_id, files)


@router.get(
    "/knowledge-bases/{kb_id}/documents",
    response_model=KnowledgeBaseDocumentListResponse,
)
async def list_kb_documents(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
):
    items, total = await knowledge_base_service.list_kb_documents(db, kb_id)
    return KnowledgeBaseDocumentListResponse(items=items, total=total)


@router.delete("/knowledge-base-documents/{doc_id}", status_code=204)
async def delete_kb_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    await knowledge_base_service.delete_kb_document(db, doc_id)
