from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    python_executable: str = "python"


settings = Settings()
