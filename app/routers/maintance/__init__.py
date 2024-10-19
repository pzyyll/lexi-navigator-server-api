from fastapi import APIRouter


router = APIRouter(prefix="/maintance", tags=["maintance"])

from . import webhook
