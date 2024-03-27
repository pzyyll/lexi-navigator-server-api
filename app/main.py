import mongoengine as mongodb

from fastapi import FastAPI

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from .settings import settings
from .routers.api import router as api_router
from .routers.index import router as index_router
from .utils.limiter import limiter


mongodb.connect(host=settings.mongodb_url, alias="default")

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(api_router)
app.include_router(index_router)
