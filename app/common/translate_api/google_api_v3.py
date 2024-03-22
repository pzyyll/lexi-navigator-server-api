# -*- coding:utf-8 -*-
# @Date: "2024-02-19"
# @Description: google translate api v3

import six
import html
import logging
import os
import pathlib

from functools import lru_cache
from langdetect import detect

from google.cloud import translate
from .base_api import BaseTranslateAPI, Language, TranslateResult, DetectLanguage


class MimeType(object):
    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    HTML = 'text/html'
    PLAIN = 'text/plain'


class GoogleAPIV3(BaseTranslateAPI):
    DEFAULT_TIMEOUT = 5

    def init(self, conf):
        super(GoogleAPIV3, self).init(conf)
        self.project_id = self.conf.get('project_id', '')
        self.auth_key = self.conf.get('auth_key', '')
        self.location = self.conf.get('location', 'global')

        if not pathlib.Path(self.auth_key).exists():
            logging.error(f"Google auth key file not found: {self.auth_key}")
            self.auth_key = ""

        self.parent = f"projects/{self.project_id}/locations/{self.location}"

        if self.project_id and self.auth_key:
            self.init_auth()
            self.client = translate.TranslationServiceClient()

    def init_auth(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.auth_key
        os.environ["PROJECT_ID"] = self.project_id

    @lru_cache(maxsize=500)
    def translate_text(self, text, to_lang, **kwargs) -> TranslateResult:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string.")

        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

        logging.debug(f'translate request text: {text}, params: {kwargs}')

        try:
            from_lang = kwargs.get('from_lang', None)
            timeout = kwargs.pop('timeout', self.DEFAULT_TIMEOUT)

            google_api_extra_params = kwargs.get('google_api_params', {})

            response = self.client.translate_text(request={
                "parent":
                self.parent,
                "contents": [text],
                "mime_type":
                google_api_extra_params.pop('mime_type', MimeType.PLAIN),
                "target_language_code":
                to_lang,
                **({
                    'source_language_code': from_lang
                } if from_lang else {}),
                **google_api_extra_params,
            },
                                                  timeout=timeout)
            translate_result = response.translations[0]
            translate_text = html.unescape(translate_result.translated_text)
            detected_language_code = translate_result.detected_language_code

            return {
                "translate_text":
                translate_text,
                **({
                    'detected_language_code': detected_language_code
                } if detected_language_code else {})
            }
        except Exception as e:
            logging.error(
                f"Failed to translate text: '{text[:50]}...'. Error: {e}")
            raise RuntimeError(
                f"Translation failed: '{text[:50]}...'|{e}") from e

    @lru_cache(maxsize=100)
    def detect_language(self, text, **kwargs) -> DetectLanguage:
        """
        Detects the language of the given text using an external API.
        
        Parameters:
        - text (str): The text for language detection.
        - kwargs: Optional arguments, including 'mime_type' for specifying the MIME type of the text.
        
        Returns:
        - dict: A dictionary containing the detected language code and the confidence level.
        
        Raises:
        - ValueError: If the text is not a string or is empty.
        - Exception: For errors encountered during the API call.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string.")

        mime_type = kwargs.get(
            'mime_type', 'text/plain')  # Default MIME type to 'text/plain'

        try:
            timeout = kwargs.pop('timeout', self.DEFAULT_TIMEOUT)
            response = self.client.detect_language(content=text,
                                                   parent=self.parent,
                                                   mime_type=mime_type,
                                                   timeout=timeout,
                                                   **kwargs)
            detected_language = response.languages[0].language_code
            confidence = response.languages[0].confidence
            return {
                'language_code': detected_language,
                'confidence': confidence
            }
        except Exception as e:
            # Log the exception details here for debugging
            logging.error(f"Failed to detect language: {e}")
            raise Exception(f"Failed to detect language: {e}")

    @lru_cache(maxsize=100)
    def list_languages(self,
                       display_language_code=None,
                       **kwargs) -> list[Language]:
        try:
            timeout = kwargs.pop('timeout', self.DEFAULT_TIMEOUT)
            response = self.client.get_supported_languages(
                parent=self.parent,
                display_language_code=display_language_code,
                timeout=timeout,
                **kwargs)
            return [{
                "language_code":
                lan.language_code,
                **({
                    "display_name": lan.display_name
                } if display_language_code else {}),
            } for lan in response.languages]
        except Exception as e:
            # Log the exception details here for debugging
            logging.error(
                f"Failed to list supported languages '{display_language_code}': {e}"
            )
            raise Exception(
                f"Failed to list supported languages '{display_language_code}': {e}"
            )
