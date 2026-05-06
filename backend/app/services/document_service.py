import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import UploadFile
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.utils.file_utils import save_upload_file, validate_file_extension
from app.utils.exceptions import NotFoundError, BadRequestError
from app.services.ai.document_parser import parse_document


async def upload_documents(
    db: AsyncSession, project_id: str, files: list[UploadFile]
) -> list[DocumentResponse]:
    results = []
    for file in files:
        try:
            file_type = validate_file_extension(file.filename)
        except ValueError as e:
            raise BadRequestError(str(e))

        file_path, file_size = await save_upload_file(file, project_id)

        doc = Document(
            project_id=project_id,
            filename=file.filename,
            file_type=file_type,
            file_path=file_path,
            file_size=file_size,
            parse_status="pending",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        # 异步解析文档
        try:
            await _parse_and_update(db, doc)
        except Exception as e:
            doc.parse_status = "failed"
            doc.parse_error = str(e)
            await db.commit()

        results.append(DocumentResponse.model_validate(doc))

    return results


async def get_documents(
    db: AsyncSession, project_id: str
) -> tuple[list[DocumentResponse], int]:
    count_result = await db.execute(
        select(func.count(Document.id)).where(Document.project_id == project_id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    # 不返回大文本字段以节省带宽
    responses = []
    for doc in docs:
        resp = DocumentResponse(
            id=doc.id,
            project_id=doc.project_id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_path=doc.file_path,
            file_size=doc.file_size,
            parse_status=doc.parse_status,
            parse_error=doc.parse_error,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
        responses.append(resp)

    return responses, total


async def get_document(db: AsyncSession, document_id: str) -> DocumentDetailResponse:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("文档")
    return DocumentDetailResponse.model_validate(doc)


async def delete_document(db: AsyncSession, document_id: str) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("文档")

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    await db.commit()


async def reparse_document(db: AsyncSession, document_id: str) -> DocumentResponse:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("文档")

    doc.parse_status = "pending"
    doc.parse_error = None
    await db.commit()

    try:
        await _parse_and_update(db, doc)
    except Exception as e:
        doc.parse_status = "failed"
        doc.parse_error = str(e)
        await db.commit()

    return DocumentResponse.model_validate(doc)


async def _parse_and_update(db: AsyncSession, doc: Document) -> None:
    doc.parse_status = "parsing"
    await db.commit()

    parse_result = await parse_document(doc.file_path, doc.file_type)

    doc.raw_text = parse_result.raw_text
    doc.parsed_markdown = parse_result.markdown
    doc.parse_status = "completed"
    await db.commit()
