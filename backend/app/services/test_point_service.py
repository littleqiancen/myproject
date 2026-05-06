from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.test_point import TestPoint
from app.models.test_case import TestCase
from app.schemas.test_point import (
    TestPointCreate, TestPointUpdate, TestPointResponse
)
from app.utils.exceptions import NotFoundError


async def get_test_points(
    db: AsyncSession,
    project_id: str,
    category: str | None = None,
    priority: str | None = None,
    status: str = "active",
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[TestPointResponse], int]:
    query = select(TestPoint).where(
        TestPoint.project_id == project_id,
        TestPoint.status == status,
    )
    count_query = select(func.count(TestPoint.id)).where(
        TestPoint.project_id == project_id,
        TestPoint.status == status,
    )

    if category:
        query = query.where(TestPoint.category == category)
        count_query = count_query.where(TestPoint.category == category)
    if priority:
        query = query.where(TestPoint.priority == priority)
        count_query = count_query.where(TestPoint.priority == priority)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(TestPoint.sort_order, TestPoint.created_at.desc())
        .offset(skip).limit(limit)
    )
    points = result.scalars().all()

    responses = []
    for p in points:
        tc_count = (await db.execute(
            select(func.count(TestCase.id)).where(TestCase.test_point_id == p.id)
        )).scalar()

        resp = TestPointResponse.model_validate(p)
        resp.test_case_count = tc_count
        responses.append(resp)

    return responses, total


async def get_test_point(db: AsyncSession, point_id: str) -> TestPointResponse:
    result = await db.execute(select(TestPoint).where(TestPoint.id == point_id))
    point = result.scalar_one_or_none()
    if not point:
        raise NotFoundError("测试点")
    return TestPointResponse.model_validate(point)


async def create_test_point(
    db: AsyncSession, project_id: str, data: TestPointCreate
) -> TestPointResponse:
    point = TestPoint(
        project_id=project_id,
        is_manual_edit=True,
        **data.model_dump(),
    )
    db.add(point)
    await db.commit()
    await db.refresh(point)
    return TestPointResponse.model_validate(point)


async def update_test_point(
    db: AsyncSession, point_id: str, data: TestPointUpdate
) -> TestPointResponse:
    result = await db.execute(select(TestPoint).where(TestPoint.id == point_id))
    point = result.scalar_one_or_none()
    if not point:
        raise NotFoundError("测试点")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(point, key, value)
    point.is_manual_edit = True

    await db.commit()
    await db.refresh(point)
    return TestPointResponse.model_validate(point)


async def delete_test_point(db: AsyncSession, point_id: str) -> None:
    result = await db.execute(select(TestPoint).where(TestPoint.id == point_id))
    point = result.scalar_one_or_none()
    if not point:
        raise NotFoundError("测试点")

    await db.delete(point)
    await db.commit()


async def batch_delete_test_points(db: AsyncSession, ids: list[str]) -> int:
    count = 0
    for point_id in ids:
        result = await db.execute(select(TestPoint).where(TestPoint.id == point_id))
        point = result.scalar_one_or_none()
        if point:
            await db.delete(point)
            count += 1
    await db.commit()
    return count
