from fastapi import APIRouter
from app.modules.user.api import router as user_router
from app.modules.forms.api import router as forms_router
from app.modules.forms.api_admin import router as forms_admin_router
from app.modules.gpt_module.api import router as gpt_module_router

router = APIRouter()
router.include_router(user_router, prefix = "/users", tags = ["users"])
router.include_router(forms_router, prefix= "/forms", tags = ["forms"])
router.include_router(forms_admin_router, prefix= "/forms/admin", tags = ["forms-admin"])
router.include_router(gpt_module_router, prefix= "/gpt_module", tags=["gpt_module"])
