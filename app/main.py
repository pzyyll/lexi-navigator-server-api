import mongoengine as mongodb

from fastapi import FastAPI
from .settings import settings
from .routers.api import router as api_router
from .routers.index import router as index_router

mongodb.connect(host=settings.mongodb_url, alias="default")

app = FastAPI()
app.include_router(api_router)
app.include_router(index_router)
