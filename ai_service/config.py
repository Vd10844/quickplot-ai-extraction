# ai_service/config.py
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    AI_ENABLED: bool = True
    MAX_FILE_SIZE_MB: int = 10

    SUPPORTED_EXTENSIONS: tuple[str, ...] = (
        ".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"
    )

    class Config:
        env_prefix = "AI_"
        env_file = ".env"


ai_settings = AISettings()
