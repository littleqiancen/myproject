from fastapi import APIRouter
from app.api.v1.projects import router as projects_router
from app.api.v1.documents import router as documents_router
from app.api.v1.test_points import router as test_points_router
from app.api.v1.test_cases import router as test_cases_router
from app.api.v1.ai_operations import router as ai_router
from app.api.v1.knowledge_bases import router as kb_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(projects_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(test_points_router)
api_v1_router.include_router(test_cases_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(kb_router)
