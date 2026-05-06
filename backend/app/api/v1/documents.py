from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentDetailResponse
from app.services import document_service

router = APIRouter(tags=["文档管理"])


@router.post("/projects/{project_id}/documents/upload", response_model=list[DocumentResponse])
async def upload_documents(
    project_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await document_service.upload_documents(db, project_id, files)


@router.get("/projects/{project_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    items, total = await document_service.get_documents(db, project_id)
    return DocumentListResponse(items=items, total=total)


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await document_service.get_document(db, document_id)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    await document_service.delete_document(db, document_id)


@router.post("/documents/{document_id}/reparse", response_model=DocumentResponse)
async def reparse_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await document_service.reparse_document(db, document_id)
