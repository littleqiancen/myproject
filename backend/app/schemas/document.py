from pydantic import BaseModel, Field
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int | None = None


class DocumentResponse(DocumentBase):
    id: str
    project_id: str
    file_path: str
    raw_text: str | None = None
    parsed_markdown: str | None = None
    parse_status: str
    parse_error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class DocumentDetailResponse(DocumentResponse):
    """文档详情，包含完整解析文本"""
    pass
