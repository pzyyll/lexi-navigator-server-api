from fastapi import APIRouter
from .chat import router as chat_router
from .auth import router as auth_router
from .translate import router as translate_router
from .search import router as search_router

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(chat_router)
router.include_router(auth_router)
router.include_router(translate_router)
router.include_router(search_router)
