from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.models.project import Project
from app.models.document import Document
from app.models.test_point import TestPoint
from app.models.test_case import TestCase
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStats
from app.utils.exceptions import NotFoundError


async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 20) -> tuple[list[ProjectResponse], int]:
    # 获取总数
    count_result = await db.execute(select(func.count(Project.id)))
    total = count_result.scalar()

    # 获取项目列表
    result = await db.execute(
        select(Project).order_by(Project.updated_at.desc()).offset(skip).limit(limit)
    )
    projects = result.scalars().all()

    # 获取每个项目的统计
    responses = []
    for project in projects:
        stats = await _get_project_stats(db, project.id)
        resp = ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            stats=stats,
        )
        responses.append(resp)

    return responses, total


async def get_project(db: AsyncSession, project_id: str) -> ProjectResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("项目")

    stats = await _get_project_stats(db, project.id)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stats=stats,
    )


async def create_project(db: AsyncSession, data: ProjectCreate) -> ProjectResponse:
    project = Project(name=data.name, description=data.description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


async def update_project(db: AsyncSession, project_id: str, data: ProjectUpdate) -> ProjectResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("项目")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)

    stats = await _get_project_stats(db, project.id)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stats=stats,
    )


async def delete_project(db: AsyncSession, project_id: str) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("项目")

    await db.delete(project)
    await db.commit()


async def _get_project_stats(db: AsyncSession, project_id: str) -> ProjectStats:
    doc_count = await db.execute(
        select(func.count(Document.id)).where(Document.project_id == project_id)
    )
    tp_count = await db.execute(
        select(func.count(TestPoint.id)).where(
            TestPoint.project_id == project_id, TestPoint.status == "active"
        )
    )
    tc_count = await db.execute(
        select(func.count(TestCase.id)).where(TestCase.project_id == project_id)
    )
    return ProjectStats(
        document_count=doc_count.scalar(),
        test_point_count=tp_count.scalar(),
        test_case_count=tc_count.scalar(),
    )
