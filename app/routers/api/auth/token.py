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


class Token(BaseModel):
    access_token: str
    token_type: str


async def create_access_token(userid):
    to_encode = {
        "sub": str(userid),
        "exp": utc_now_offset(days=settings.token_expire_days)
    }
    return jwt.encode(to_encode,
                      settings.secret_key,
                      algorithm=settings.token_algorithm)


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
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user: UserInDB = await UserInDB.async_find_one(userid=userid)
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Invalid token, user not found")
    return user
