from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False,
                                      env_prefix="LN_",
                                      env_file=".env",
                                      validate_default=False)

    app_name: str = "Lexi Navigator"
    mongodb_url: str = "mongodb://localhost:27017/lexi_navigator"
    cftoken: str = ""
    signup_secret: str = ""
    secret_key: str


settings = Settings()
