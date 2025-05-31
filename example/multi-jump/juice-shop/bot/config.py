from loguru import logger
from pydantic import Field
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class Settings(YamlBaseSettings):
    debug: bool = Field(default=False)
    host_port: str = Field(default="server:3000")
    attack: bool = Field(default=False)
    self_host: str = Field(default="localhost")

    model_config = SettingsConfigDict(yaml_file="config.yaml", extra="ignore")


settings = Settings()  # type: ignore
logger.info(settings)
