from . import router
from ..auth.token import get_token_user
from app.models.user import UserInDB

from fastapi import Request, Depends
from pydantic import BaseModel
from pydantic import Field


# class TranslateRequest(BaseModel):
#     text: list[str]
#     sl: str | None = Field(default=None, alias="source_language", title="source language")
#     tl: str | None = Field(default=None, alias="target_language", title="target language")


class TranslateResponse(BaseModel):
    text: list[str]
    detected_source_language: str | None


@router.get("/text", response_model=TranslateResponse, response_model_exclude_unset=True)
async def translate_text(text: str, sl: str = None, tl: str = None,
                         user: UserInDB = Depends(get_token_user)):
    # print("translate_text Content", request_data)
    print("translate_text User:", user)
    return TranslateResponse(text=["This is a test translation"], detected_source_language="en")
