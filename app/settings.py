from pydantic_settings import BaseSettings, SettingsConfigDict

from datetime import datetime, timedelta

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False,
                                      env_prefix="LN_",
                                      env_file=".env",
                                      validate_default=False)

    app_name: str = "Lexi Navigator"
    mongodb_url: str = "mongodb://localhost:27017/lexi_navigator"
    cftoken: str = ""
    cftoken_enable: bool = False
    cftoken_url: str = ""
    signup_secret: str = ""
    secret_key: str
    token_algorithm: str | None = "HS256"
    token_expire_days: int = 15


settings = Settings()
