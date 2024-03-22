from . import router
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form

from http import HTTPStatus

from app.settings import settings
from app.models.user import UserInDB
from .token import Token, create_access_token

import httpx


async def verify_cftoken(cftoken: str):
    if not cftoken:
        raise HTTPException(status_code=400, detail="Captcha token required")
    cftoken_check_data = {"secret": settings.cftoken, "response": cftoken}
    cftoken_check_url = settings.cftoken_url
    async with httpx.AsyncClient() as client:
        response = await client.post(cftoken_check_url,
                                     json=cftoken_check_data)
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(status_code=400,
                                detail="Incorrect captcha token")
        response_data = response.json()
        if not response_data["success"]:
            raise HTTPException(status_code=400,
                                detail="Incorrect captcha token")
    return True


@router.api_route("/login", methods=["POST"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                cftoken: str | None = Form(default=None)):
    # print("login form_data", form_data)
    # print("login cftoken", cftoken)
    if settings.cftoken_enable:
        # check captcha token
        await verify_cftoken(cftoken)
    user: UserInDB = await UserInDB.async_find_one(username=form_data.username)
    # print("login user", user)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not user.verify_passwd(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token = await create_access_token(user.userid)
    return Token(access_token=token, token_type="bearer")
