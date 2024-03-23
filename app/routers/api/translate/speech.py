import io
import asyncio
import pathlib
from . import router
from fastapi import Depends
from fastapi.responses import StreamingResponse
from ..auth.token import get_token_user
from app.models.user import UserInDB

from app.common.speech_api.gspeech import GSpeechAsyncClient
from app.settings import settings

from urllib.parse import quote

gspeech = GSpeechAsyncClient()

relative_temp = "temp/text-to-speech"
temp_dir = pathlib.Path(settings.static_path, relative_temp).resolve()


async def get_mp3_response(text, language_code, user: UserInDB):
    audio_content = await gspeech.text_to_speech(text, language_code)
    # file_name = f"{user.userid}.mp3"

    # def _write_file():
    #     temp_dir.mkdir(parents=True, exist_ok=True)
    #     file = temp_dir.joinpath(file_name)
    #     file.write_bytes(audio_content)

    # await asyncio.get_event_loop().run_in_executor(None, _write_file)

    # return {"url_relative": f"{relative_temp}/{file_name}"}
    streamfile = await asyncio.get_event_loop().run_in_executor(
        None, io.BytesIO, audio_content
    )
    return StreamingResponse(
        streamfile,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=text-to-speech.mp3"},
    )


@router.get("/text-to-speech")
async def text_to_speech(
    text: str, language_code: str, user: UserInDB = Depends(get_token_user)
):
    return await get_mp3_response(text, language_code, user)
