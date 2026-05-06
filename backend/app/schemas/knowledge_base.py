from pydantic import BaseModel, Field
from datetime import datetime


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., max_length=255, description="知识库名称")
    description: str | None = Field(None, description="知识库描述")


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None


class KnowledgeBaseDocumentResponse(BaseModel):
    id: str
    knowledge_base_id: str
    filename: str
    file_type: str
    file_size: int | None
    chunk_count: int
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeBaseResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str | None
    document_count: int
    chunk_count: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeBaseListResponse(BaseModel):
    items: list[KnowledgeBaseResponse]
    total: int


class KnowledgeBaseDocumentListResponse(BaseModel):
    items: list[KnowledgeBaseDocumentResponse]
    total: int
