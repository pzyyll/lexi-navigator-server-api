from fastapi import APIRouter

router = APIRouter(prefix="/search")

from . import gsearch
