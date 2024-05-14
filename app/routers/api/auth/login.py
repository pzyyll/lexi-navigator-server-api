from . import router
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from fastapi import Response
from fastapi.responses import RedirectResponse

from http import HTTPStatus

from app.settings import settings
from app.models.user import UserInDB
from app.models.response import Token, LoginResponse
from .token import create_access_token

import httpx


async def verify_cftoken(cftoken: str):
    if not cftoken:
        raise HTTPException(status_code=400, detail="Captcha token required")
    cftoken_check_data = {"secret": settings.cftoken, "response": cftoken}
    cftoken_check_url = settings.cftoken_url
    async with httpx.AsyncClient() as client:
        response = await client.post(cftoken_check_url, json=cftoken_check_data)
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(status_code=400, detail="Incorrect captcha token")
        response_data = response.json()
        if not response_data["success"]:
            raise HTTPException(status_code=400, detail="Incorrect captcha token")
    return True


async def login_auth(
        form_data: OAuth2PasswordRequestForm = Depends(),
        cftoken: str | None = Form(default=None),
):
    if settings.cftoken_enable:
        # check captcha token
        await verify_cftoken(cftoken)
    user: UserInDB = await UserInDB.async_find_one(username=form_data.username)
    # print("login user", user)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not user.verify_passwd(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    user.login_token_version += 1
    user.activated = True
    await user.async_save()
    token = await create_access_token(user.userid, user.login_token_version)
    return Token(access_token=token, token_type="bearer")


@router.api_route("/login", methods=["POST"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    cftoken: str | None = Form(default=None),
):
    return await login_auth(form_data, cftoken)


@router.api_route("/login_cookie", methods=["POST"])
async def login_cookie(
        form_data: OAuth2PasswordRequestForm = Depends(),
        cftoken: str | None = Form(default=None),
        response: Response = None,
):
    token = await login_auth(form_data, cftoken)
    response.set_cookie(
        "access_token",
        token.access_token,
        httponly=True,
        max_age=60 * 60 * 24 * 30,
        secure=settings.http_secure,
        samesite="lax",
    )
    return {"detail": "login success"}
