import httpx
import logging

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from . import router
from app.settings import settings


TARGET_URL = "https://customsearch.googleapis.com/customsearch/v1"


@router.get("/google")
async def search(request: Request):
    headers = dict(request.headers)
    headers.pop("host", None)

    params = dict(request.query_params)
    params["cx"] = settings.google_search_id
    params["key"] = settings.google_search_key

    data = await request.body()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=TARGET_URL,
                params=params,
                headers=headers,
                content=data,
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers["Content-Type"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
