from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    MODEL_NAME: str = "qwen3.6-plus"
    MAX_UPLOAD_MB: int = 20
    ALLOWED_ORIGINS: str = "*"

    BASE_DIR: Path = Path(__file__).resolve().parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    PAPERS_DIR: Path = STORAGE_DIR / "papers"
    STUDENT_IMGS_DIR: Path = STORAGE_DIR / "student_imgs"
    DB_PATH: Path = STORAGE_DIR / "app.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

for d in (settings.STORAGE_DIR, settings.PAPERS_DIR, settings.STUDENT_IMGS_DIR):
    d.mkdir(parents=True, exist_ok=True)
