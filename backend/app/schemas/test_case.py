from pydantic import BaseModel, Field, field_validator
import json
from datetime import datetime


class TestStepSchema(BaseModel):
    step_number: int
    action: str
    expected_result: str


class TestCaseBase(BaseModel):
    title: str = Field(..., max_length=500)
    preconditions: str | None = None
    steps: list[TestStepSchema]
    priority: str | None = None
    case_type: str | None = None

    @field_validator("steps", mode="before")
    @classmethod
    def parse_steps(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class TestCaseUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    preconditions: str | None = None
    steps: list[TestStepSchema] | None = None
    priority: str | None = None
    case_type: str | None = None
    status: str | None = None


class TestCaseResponse(TestCaseBase):
    id: str
    project_id: str
    test_point_id: str
    status: str = "draft"
    generation_batch_id: str | None = None
    created_at: datetime
    updated_at: datetime
    test_point_title: str | None = None

    model_config = {"from_attributes": True}


class TestCaseListResponse(BaseModel):
    items: list[TestCaseResponse]
    total: int
