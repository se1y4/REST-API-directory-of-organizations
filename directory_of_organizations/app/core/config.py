import os
import secrets

from pydantic import Field


from pydantic import (
    BaseModel,
    PostgresDsn,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


def get_config_path() -> str:
    base_dir = os.path.dirname(__file__)
    config_path = os.getenv("CONFIG_PATH", "/../../config.yaml")
    return base_dir + config_path


class DatabaseSettings(BaseModel):
    SERVER: str
    PORT: int = 5432
    USER: str | None = None
    PASSWORD: str | None = None
    DB: str = ""


class SecuritySettings(BaseModel):
    API_TOKEN: str = Field(default_factory=lambda: secrets.token_urlsafe(32))


class ServiceSettings(BaseModel):
    API_PREFIX: str = "/api/"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=get_config_path(),
        env_ignore_empty=True,
        extra="ignore",
    )

    service: ServiceSettings
    database: DatabaseSettings
    security: SecuritySettings

    DEBUG: bool = False

    @computed_field
    def MAIN_DATABASE_URI(self) -> PostgresDsn:
        multi_host_url = MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.database.USER,
            password=self.database.PASSWORD,
            host=self.database.SERVER,
            port=self.database.PORT,
            path=self.database.DB,
        )
        return PostgresDsn(multi_host_url)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


settings = Settings() # type: ignore