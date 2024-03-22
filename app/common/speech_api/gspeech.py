# -*- coding:utf-8 -*-
# @Date: "2024-03-23"
# @Description: google speech api

from google.cloud import texttospeech


class GSpeechAsyncClient:
    def __init__(self, conf=None):
        self.init(conf)

    def init(self, conf=None):
        self.conf = conf.copy if conf else {}
        self.client = texttospeech.TextToSpeechAsyncClient()

    async def text_to_speech(self, text, language_code):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3)
        response = await self.client.synthesize_speech(input=synthesis_input,
                                                       voice=voice,
                                                       audio_config=audio_config)
        return response.audio_content
