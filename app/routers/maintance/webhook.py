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

    logger.info("Pulling the latest changes from the repository")

    try:
        os.chdir(app_path)
    except Exception as e:
        logger.error(f"Failed to change directory to {app_path}: {e}")
        return {"message": "failed to change directory"}

    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    if result.returncode == 0:
        logger.info(f"Git pull successful: {result.stdout}")
    else:
        logger.error(f"Git pull failed: {result.stderr}")
        return {"message": "git pull failed"}

    logger.info(f"Restarting the application {settings.app_name}")
    try:
        subprocess.Popen(["sudo", "systemctl", "restart", settings.app_name], shell=False)
    except Exception as e:
        logger.error(f"Failed to restart the application: {e}")
        return {"message": "failed to restart application"}

    return {"message": "ok"}
