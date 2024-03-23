import io
import asyncio
from . import router
from fastapi import Depends
from fastapi.responses import StreamingResponse
from ..auth.token import get_token_user
from app.models.user import UserInDB

from app.common.speech_api.gspeech import GSpeechAsyncClient

gspeech = GSpeechAsyncClient()


async def get_mp3_response(audio_content):
    loop = asyncio.get_event_loop()
    mp3_file_io = await loop.run_in_executor(None, io.BytesIO, audio_content)
    return StreamingResponse(
        mp3_file_io, media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=speech.mp3"})


@router.get("/text-to-speech")
async def text_to_speech(text: str, language_code: str, user: UserInDB = Depends(get_token_user)):
    audio_content = await gspeech.text_to_speech(text, language_code)
    return await get_mp3_response(audio_content)
