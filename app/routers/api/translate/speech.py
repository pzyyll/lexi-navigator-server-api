from . import router
from fastapi import Depends
from ..auth.token import get_token_user
from app.models.user import UserInDB

from app.common.speech_api.gspeech import GSpeechAsyncClient

gspeech = GSpeechAsyncClient()


@router.get("/text-to-speech")
async def text_to_speech(text: str, language_code: str, user: UserInDB = Depends(get_token_user)):
    audio_content = await gspeech.text_to_speech(text, language_code)
    return {"audio_content": audio_content}
