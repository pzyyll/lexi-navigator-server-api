from . import router
from ..auth.token import get_token_user
from app.models.user import UserInDB
from app.utils.translate import translate_api

from fastapi import Request, Depends
from pydantic import BaseModel, Field
from typing import Annotated


class TranslateRequest(BaseModel):
    text: str
    sl: str | None = Field(
        default=None, alias="source_language", title="source language"
    )
    tl: str | None = Field(
        default=None, alias="target_language", title="target language"
    )
    api_type: str | None = Field(default=None, title="api type e.g. 'google'|'deepl'")


class TranslateResponse(BaseModel):
    text: list[str]
    detected_source_language: str | None


class Language(BaseModel):
    display_name: str
    language_code: str


class DetectLanguage(BaseModel):
    language_code: str
    confidence: float


class LanguagesResponse(BaseModel):
    languages: list[Language]


@router.get(
    "/text", response_model=TranslateResponse, response_model_exclude_unset=True
)
async def translate_text(
    text: str,
    sl: Annotated[str, "source language"] = None,
    tl: Annotated[str, "target language"] = None,
    api_type: Annotated[str, "api type e.g. 'google'|'deepl'"] = None,
    user: UserInDB = Depends(get_token_user),
):
    # print("translate_text Content", request_data)
    # print("translate_text User:", user)
    async with translate_api.async_api_type_context(api_type):
        result = await translate_api.async_translate_text(
            text, to_lang=tl, from_lang=sl
        )
        return TranslateResponse(
            text=[result["translate_text"]],
            detected_source_language=result.get("detected_language_code"),
        )


@router.post(
    "/text", response_model=TranslateResponse, response_model_exclude_unset=True
)
async def translate_text_post(
    request_data: TranslateRequest,
    user: UserInDB = Depends(get_token_user),
):
    # print("translate_text Content", request_data)
    # print("translate_text User:", user)
    async with translate_api.async_api_type_context(request_data.api_type):
        result = await translate_api.async_translate_text(
            request_data.text,
            to_lang=request_data.tl,
            from_lang=request_data.sl,
        )
        return TranslateResponse(
            text=[result["translate_text"]],
            detected_source_language=result.get("detected_language_code"),
        )


@router.get("/languages")
async def languages(
    dlc: Annotated[str, "display language code"] = None,
    api_type: str = None,
    user: UserInDB = Depends(get_token_user),
):
    async with translate_api.async_api_type_context(api_type):
        results = await translate_api.async_list_languages(dlc)
        return LanguagesResponse(languages=[Language(**lang) for lang in results])


@router.get("/detect")
async def detect(
    text: str,
    api_type: str = None,
    user: UserInDB = Depends(get_token_user),
):
    async with translate_api.async_api_type_context(api_type):
        result = await translate_api.async_detect_language(text)
        return DetectLanguage(
            language_code=result["language_code"], confidence=result["confidence"]
        )
