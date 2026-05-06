from pydantic import BaseModel, Field
from datetime import datetime


class TestPointBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: str
    priority: str | None = Field(None, pattern="^P[0-3]$")
    category: str | None = None
    preconditions: str | None = None
    expected_result: str | None = None
    source_context: str | None = None


class TestPointCreate(TestPointBase):
    document_id: str | None = None


class TestPointUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    description: str | None = None
    priority: str | None = None
    category: str | None = None
    preconditions: str | None = None
    expected_result: str | None = None
    status: str | None = None
    sort_order: int | None = None


class TestPointResponse(TestPointBase):
    id: str
    project_id: str
    document_id: str | None = None
    is_manual_edit: bool = False
    generation_batch_id: str | None = None
    status: str = "active"
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime
    test_case_count: int = 0

    model_config = {"from_attributes": True}


class TestPointListResponse(BaseModel):
    items: list[TestPointResponse]
    total: int


class BatchDeleteRequest(BaseModel):
    ids: list[str]
