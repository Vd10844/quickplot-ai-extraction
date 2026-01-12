from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    AI_ENABLED: bool = True
    OCR_LANG: str = "eng"
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_EXTENSIONS: tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg")
    TESSERACT_CMD: str | None = None  # path if needed on Windows

    class Config:
        env_prefix = "AI_"        # e.g. AI_OCR_LANG
        env_file = ".env"

ai_settings = AISettings()
