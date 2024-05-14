from .base_api import BaseTranslateAPI as BaseAPI

from app.common.chatgpt_api.chatgpt_api import Chatbot


class ChatGPTAPI(BaseAPI):

    def init(self, conf):
        super(ChatGPTAPI, self).init(conf)
        self._chatbot = Chatbot()
        self._system_prompt = "You are ChatGPT, a large language model trained by OpenAI. Now you will play the role of a translator, translate the provided text and return it in JSON format, including the following fields: t[translated text], dsl[original language code]."
        self._system_detect_prompt = "You are ChatGPT, a large language model trained by OpenAI. Now you will play the role of a language detector, detect the language of the provided text and return it in JSON format, including the following fields: dsl[detected language code]."

    def detect_language(self, text, **kwargs):
        raise NotImplementedError

    def translate_text(self, text, to_lang=None, **kwargs):
        raise NotImplementedError

    def list_languages(self, display_language_code=None, **kwargs):
        raise NotImplementedError
