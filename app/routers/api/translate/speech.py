import io
import asyncio
import pathlib
from . import router
from fastapi import Depends, Request
from fastapi.responses import StreamingResponse
from ..auth.token import get_token_user
from app.models.user import UserInDB

from app.common.speech_api.gspeech import GSpeechAsyncClient
from app.settings import settings
from app.utils.limiter import limiter

from urllib.parse import quote

gspeech = GSpeechAsyncClient()


async def get_mp3_response(text, language_code, user: UserInDB):
    audio_content = await gspeech.text_to_speech(text, language_code)
    streamfile = await asyncio.get_event_loop().run_in_executor(
        None, io.BytesIO, audio_content
    )
    return StreamingResponse(
        streamfile,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=text-to-speech.mp3"},
    )


@router.get("/text-to-speech")
@limiter.limit("5/second")
async def text_to_speech(
    text: str,
    language_code: str,
    user: UserInDB = Depends(get_token_user),
    request: Request = None,
):
    return await get_mp3_response(text, language_code, user)
