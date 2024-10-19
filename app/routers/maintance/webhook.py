from fastapi import HTTPException, Request
from . import router

from app.settings import settings, app_path

import hmac
import hashlib
import subprocess
import os
import logging

logger = logging.getLogger("uvicorn")

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
    # chdir to app_path
    logger.info("Pulling the latest changes from the repository")

    os.chdir(app_path)

    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    if result.returncode == 0:
        logger.info(f"Git pull successful: {result.stdout}")
    else:
        logger.error(f"Git pull failed: {result.stderr}")

    logger.info("Restarting the application ", settings.app_name)
    subprocess.Popen(["sudo", "systemctl", "restart", settings.app_name])

    return {"message": "ok"}
