from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
ENV_FILE = REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")

    secret_key: str = "dev-insecure-secret-change-me-in-your-env-file-32bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_path: str = str(BACKEND_DIR / "data" / "app.db")
    static_dir: str = str(REPO_ROOT / "frontend" / "out")
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
