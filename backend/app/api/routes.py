from fastapi import APIRouter
from app.modules.user.api import router as user_router

router = APIRouter()
router.include_router(user_router, prefix = "/users", tags = ["users"])
