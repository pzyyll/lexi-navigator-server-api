from app.common.translate_api.proxy_api import ProxyAPIs
from libs.pyhelper.config import Config
from libs.pyhelper.singleton import ABCSingletonMeta

from app.settings import settings, path_helper

import logging


class GlobalTranslateAPI(ProxyAPIs, metaclass=ABCSingletonMeta):

    def init(self, conf):
        try:
            if settings.translate_config:
                conf = Config(path_helper.get_path(settings.translate_config))
            else:
                app_data_path = path_helper.get_path(settings.app_data_path)
                config_path = path_helper.join_paths(app_data_path, "config",
                                                     "translate_api.conf")
                conf = Config(config_path)
            data = conf.data
        except Exception as e:
            logging.error(f"Failed to load translate api config: {e}")
            data = {}
        super().init(data)


translate_api = GlobalTranslateAPI()
