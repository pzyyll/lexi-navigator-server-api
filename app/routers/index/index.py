from . import router
from fastapi.responses import HTMLResponse, FileResponse
from functools import partial

from app.settings import app_path

import os
import asyncio

index_static = os.path.join(app_path, "static/dist")


def read_file_sync(path):
    with open(path, "r") as f:
        return f.read()


async def async_read(path: str):
    loop = asyncio.get_event_loop()
    read = partial(read_file_sync, path)
    return await loop.run_in_executor(None, read)


@router.get("/{path:path}")
async def index(path: str):
    path = path.rstrip("/")
    if not path or not os.path.isfile(os.path.join(index_static, path)):
        path = "index.html"
    return FileResponse(os.path.join(index_static, path))
