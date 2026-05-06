from pydantic import BaseModel, Field
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255, description="项目名称")
    description: str | None = Field(None, description="项目描述")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None


class ProjectStats(BaseModel):
    document_count: int = 0
    test_point_count: int = 0
    test_case_count: int = 0


class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    stats: ProjectStats = ProjectStats()

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
