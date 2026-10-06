from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.project_members import router as project_members_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(project_members_router)
