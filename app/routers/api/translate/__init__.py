from fastapi import APIRouter

router = APIRouter(prefix="/translate")

from . import text