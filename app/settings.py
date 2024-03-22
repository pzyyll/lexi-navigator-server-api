from pydantic_settings import BaseSettings, SettingsConfigDict
from libs.pyhelper.path_helper import PathHelper
import os

app_path = os.path.dirname(os.path.abspath(__file__))
path_helper = PathHelper()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False,
                                      env_prefix="LN_",
                                      env_file=".env-release",
                                      validate_default=False)

    app_name: str = "Lexi Navigator"
    mongodb_url: str = "mongodb://localhost:27017/test"
    cftoken: str = ""
    cftoken_enable: bool = False
    cftoken_url: str = ""
    signup_secret: str = ""
    secret_key: str
    token_algorithm: str | None = "HS256"
    token_expire_days: int = 15
    app_data_path: str = "../app-data"
    translate_config: str | None = None


settings = Settings()
