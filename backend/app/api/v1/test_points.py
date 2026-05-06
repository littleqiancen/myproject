from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.test_point import (
    TestPointCreate, TestPointUpdate, TestPointResponse,
    TestPointListResponse, BatchDeleteRequest,
)
from app.services import test_point_service

router = APIRouter(tags=["测试点管理"])


@router.get("/projects/{project_id}/test-points", response_model=TestPointListResponse)
async def list_test_points(
    project_id: str,
    category: str | None = None,
    priority: str | None = None,
    status: str = "active",
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    items, total = await test_point_service.get_test_points(
        db, project_id, category=category, priority=priority,
        status=status, skip=skip, limit=limit,
    )
    return TestPointListResponse(items=items, total=total)


@router.post("/projects/{project_id}/test-points", response_model=TestPointResponse, status_code=201)
async def create_test_point(
    project_id: str,
    data: TestPointCreate,
    db: AsyncSession = Depends(get_db),
):
    return await test_point_service.create_test_point(db, project_id, data)


@router.get("/test-points/{point_id}", response_model=TestPointResponse)
async def get_test_point(
    point_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await test_point_service.get_test_point(db, point_id)


@router.put("/test-points/{point_id}", response_model=TestPointResponse)
async def update_test_point(
    point_id: str,
    data: TestPointUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await test_point_service.update_test_point(db, point_id, data)


@router.delete("/test-points/{point_id}", status_code=204)
async def delete_test_point(
    point_id: str,
    db: AsyncSession = Depends(get_db),
):
    await test_point_service.delete_test_point(db, point_id)


@router.post("/test-points/batch-delete")
async def batch_delete_test_points(
    data: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    count = await test_point_service.batch_delete_test_points(db, data.ids)
    return {"deleted": count}
