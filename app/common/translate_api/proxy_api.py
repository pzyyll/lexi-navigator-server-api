# -*- coding:utf-8 -*-
# @Date: "2024-02-15"
# @Description: APIs Proxy

import logging
import asyncio
import functools
from collections import OrderedDict
from langdetect import detect

from libs.pyhelper.singleton import ABCSingletonMeta
from libs.pyhelper.proxy_helper import ProxyWorkerPool

from .base_api import (
    BaseTranslateAPI,
    TranslateError,
    DetectLanguage,
    Language,
    TranslateResult,
)
from .google_api_v3 import GoogleAPIV3 as GoogleAPI
from .baidu_api import BaiduAPI

from contextlib import contextmanager, asynccontextmanager

# class ApiTypeContext(object):

#     def __init__(self, api, api_type):
#         self.api_type = api_type
#         self.api = api

#     def __enter__(self):
#         self.api.set_api_type(self.api_type)
#         return self.api

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.api.set_api_type(None)


class TranslateAPIProxyExecutor(BaseTranslateAPI):

    @classmethod
    def create(cls, proxy, proxy_cls, *args, **kwargs):
        proxy_executor = cls()
        proxy_executor._set_worker_info(proxy, proxy_cls, *args, **kwargs)
        return proxy_executor

    def init(self, conf):
        super().init(conf)
        self._proxy_worker = None
        self.proxy = None
        self.proxy_cls = None
        self.proxy_cls_args = ()
        self.proxy_cls_kwargs = {}

    def _set_worker_info(self, proxy, proxy_cls, *proxy_cls_args, **proxy_cls_kwargs):
        self.proxy = proxy
        self.proxy_cls = proxy_cls
        self.proxy_cls_args = proxy_cls_args
        self.proxy_cls_kwargs = proxy_cls_kwargs

    def _init_worker(self):
        if self.proxy and self.proxy_cls:
            # 需要代理访问的API，创建一个新的代理进程池处理，代理需要设置全局的socket.socket避免多线程下代理设置污染主进程
            self._proxy_worker = ProxyWorkerPool()
            self._proxy_worker.set_proxy_info(
                self.proxy,
                self.proxy_cls,
                *self.proxy_cls_args,
                **self.proxy_cls_kwargs,
            )

    @property
    def proxy_worker(self):
        if not self._proxy_worker:
            self._init_worker()
        return self._proxy_worker

    def _execute(self, func, *args, **kwargs):
        if self.proxy_worker:
            result = self.proxy_worker.submit(func, *args, **kwargs)
            return result.result()

    def translate_text(self, text, to_lang=None, **kwargs):
        return self._execute("translate_text", text, to_lang, **kwargs)

    def detect_language(self, text, **kwargs):
        return self._execute("detect_language", text, **kwargs)

    def list_languages(self, display_language_code=None, **kwargs):
        return self._execute("list_languages", display_language_code, **kwargs)


class GlobalGoobleAPI(GoogleAPI, metaclass=ABCSingletonMeta):
    pass


class ProxyAPIs(BaseTranslateAPI):
    GOOGLE = "google"
    BAIDU = "baidu"

    API_TYPE = OrderedDict({GOOGLE: GlobalGoobleAPI, BAIDU: BaiduAPI})

    @property
    def _default_api(self):
        return self._apis.get(self.api_type, None)

    def init(self, conf):
        super(ProxyAPIs, self).init(conf)
        self._apis = OrderedDict({})
        for api_type, conf in self.conf.items():
            try:
                api_class = self.API_TYPE.get(api_type)
                api = (
                    TranslateAPIProxyExecutor.create(conf.get("proxy"), api_class, conf)
                    if "proxy" in conf
                    else api_class(conf)
                )
                self._apis[api_type] = api
            except Exception as e:
                logging.error(f"Invalid API type: {api_type} | {e}")
                continue

    def set_api_type(self, api_type=None):
        super(ProxyAPIs, self).set_api_type(None)
        if api_type and api_type not in self._apis:
            raise ValueError("Invalid API type.")

    @contextmanager
    def api_type_context(self, api_type):
        try:
            self.set_api_type(api_type)
            yield self
        finally:
            self.set_api_type(None)

    @asynccontextmanager
    async def async_api_type_context(self, api_type):
        try:
            self.set_api_type(api_type)
            yield self
        finally:
            self.set_api_type(None)

    async def async_run(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        partial_func = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, partial_func)

    async def async_detect_language(self, text, **kwargs) -> DetectLanguage:
        return await self.async_run(self.detect_language, text, **kwargs)

    async def async_translate_text(
        self, text, to_lang=None, **kwargs
    ) -> TranslateResult:
        return await self.async_run(self.translate_text, text, to_lang, **kwargs)

    async def async_list_languages(
        self, display_language_code=None, **kwargs
    ) -> list[Language]:
        return await self.async_run(
            self.list_languages, display_language_code, **kwargs
        )

    def detect_language(self, text, **kwargs):
        if self._default_api:
            try:
                return self._default_api.detect_language(text, **kwargs)
            except Exception as exc:
                raise TranslateError("Default API failed to detect language.") from exc

        for _, api in self._apis.items():
            try:
                return api.detect_language(text, **kwargs)
            except Exception as exc:
                logging.warning(f"API {api} failed to detect language: {exc}")
                continue
        raise TranslateError("All APIs failed to detect language.")

    def translate_text(self, text, to_lang=None, **kwargs):
        if not to_lang:
            from_lang = kwargs.get("from_lang", None)
            if not from_lang:
                from_lang = self.detect_language(text).get("language_code")
            to_lang = "en" if from_lang.lower().startswith("zh") else "zh"

        if self._default_api:
            try:
                return self._default_api.translate_text(text, to_lang, **kwargs)
            except Exception as exc:
                raise TranslateError("Default API failed to translate text.") from exc

        for api_type, api in self._apis.items():
            try:
                result = api.translate_text(text, to_lang, **kwargs)
                result["from_api_type"] = api_type
                return result
            except Exception as e:
                logging.warning(f"API {api} failed to translate text: {e}")
                continue
        raise TranslateError("All APIs failed to translate text.")

    def list_languages(self, display_language_code=None) -> list[Language]:
        if self._default_api:
            try:
                return self._default_api.list_languages(display_language_code)
            except Exception as exc:
                raise TranslateError("Default API failed to list languages.") from exc

        for api_type, api in self._apis.items():
            try:
                return api.list_languages(display_language_code)
            except Exception as e:
                logging.warning(f"API {api} failed to list languages: {e}")
                continue
        raise TranslateError("All APIs failed to list languages.")

    def local_detect_language(self, text, **kwargs) -> DetectLanguage:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string.")
        try:
            detected_language = detect(text)
            logging.debug(f"detected language: {detected_language}")
            if detected_language.startswith("zh"):
                detected_language = "zh"
            return {"language_code": detected_language, "confidence": 1.0}
        except Exception as e:
            # Log the exception details here for debugging
            logging.error(f"Failed to detect language: {e}")
            raise Exception(f"Failed to detect language: {e}")
