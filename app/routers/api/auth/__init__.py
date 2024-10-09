from fastapi import APIRouter

router = APIRouter(prefix="/auth")

from . import login, logout, signup