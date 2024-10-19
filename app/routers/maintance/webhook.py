from fastapi import HTTPException, Request
from . import router

from app.settings import settings

import hmac
import hashlib


async def verify_signature(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=403, detail="Missing signature header")

    secret = settings.webhook_secret
    if not secret:
        raise HTTPException(status_code=403, detail="Missing server secret")

    body = await request.body()
    h = hmac.new(secret.encode(), body, hashlib.sha256)
    expected_signature = f"sha256={h.hexdigest()}"
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    return True


@router.post("/push")
async def push(request: Request):
    await verify_signature(request)

    # Do something with the push event
    

    return {"message": "ok"}
