from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.test_case import TestCaseUpdate, TestCaseResponse, TestCaseListResponse
from app.services import test_case_service
import io

router = APIRouter(tags=["测试用例管理"])


@router.get("/projects/{project_id}/test-cases", response_model=TestCaseListResponse)
async def list_test_cases(
    project_id: str,
    test_point_id: str | None = None,
    priority: str | None = None,
    case_type: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    items, total = await test_case_service.get_test_cases(
        db, project_id, test_point_id=test_point_id, priority=priority,
        case_type=case_type, status=status, skip=skip, limit=limit,
    )
    return TestCaseListResponse(items=items, total=total)


@router.get("/test-cases/{case_id}", response_model=TestCaseResponse)
async def get_test_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await test_case_service.get_test_case(db, case_id)


@router.put("/test-cases/{case_id}", response_model=TestCaseResponse)
async def update_test_case(
    case_id: str,
    data: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await test_case_service.update_test_case(db, case_id, data)


@router.delete("/test-cases/{case_id}", status_code=204)
async def delete_test_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
):
    await test_case_service.delete_test_case(db, case_id)


@router.get("/projects/{project_id}/test-cases/export")
async def export_test_cases(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    excel_bytes = await test_case_service.export_test_cases_excel(db, project_id)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=test_cases.xlsx"},
    )
