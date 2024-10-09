from fastapi import APIRouter

router = APIRouter(prefix="/chat")

from . import completion