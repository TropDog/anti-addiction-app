from fastapi import APIRouter
from app.modules.user.api import router as user_router
from app.modules.forms.api import router as forms_router
print("FORMS ROUTER:", forms_router.routes)
router = APIRouter()
router.include_router(user_router, prefix = "/users", tags = ["users"])
router.include_router(forms_router, prefix= "/forms", tags = ["forms"])
