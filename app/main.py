import mongoengine as mongodb

from fastapi import FastAPI

from .settings import settings
from .routers.api import router as api_router

mongodb.connect(host=settings.mongodb_url, alias="default")

app = FastAPI()
app.include_router(api_router)
