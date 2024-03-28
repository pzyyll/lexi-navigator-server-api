from . import router
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt

from app.models.user import UserInDB
from app.settings import settings
from app.common.time import utc_now_offset

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class EnumTokenType:
    Login = "login"
    Api = "api"


class Token(BaseModel):
    access_token: str
    token_type: str


async def create_token(payload: dict):
    to_encode = payload.copy()
    return jwt.encode(to_encode,
                      settings.secret_key,
                      algorithm=settings.token_algorithm)


async def create_access_token(userid, ver=1):
    return await create_token({
        "sub": str(userid),
        "aty": EnumTokenType.Login,
        "ver": ver,
        "exp": utc_now_offset(days=settings.token_expire_days)
    })


async def get_token_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,
                             settings.secret_key,
                             algorithms=[settings.token_algorithm])
        userid: str = payload.get("sub")
        if userid is None:
            raise HTTPException(status_code=401, detail="Invalid token userid")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")
    user: UserInDB = await UserInDB.async_find_one(userid=userid)
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Invalid token, user not found")
    token_type = payload.get("aty")
    if token_type == EnumTokenType.Login:
        if user.login_token_version != payload.get("ver"):
            raise HTTPException(status_code=401,
                                detail="Invalid token version")
    elif token_type == EnumTokenType.Api:
        if user.api_token_version != payload.get("ver"):
            raise HTTPException(status_code=401,
                                detail="Invalid token version")
    else:
        raise HTTPException(status_code=401, detail=f"Invalid token type, {token_type}")
    return user


@router.get("/get_api_token", response_model=Token)
async def get_api_token(user: UserInDB = Depends(get_token_user)):
    user.api_token_version += 1
    await user.async_save()
    token = await create_token({
        "sub": str(user.userid),
        "ver": user.api_token_version,
        "aty": EnumTokenType.Api
    })
    return Token(access_token=token, token_type="bearer")
