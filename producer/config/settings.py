from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── Kafka ────────────────────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092")
    KAFKA_TOPIC: str = Field(default="filtered-words")
    KAFKA_CLIENT_ID: str = Field(default="word-producer")

    # ── Wikipedia ────────────────────────────────────────────────────────────
    WIKIPEDIA_LANGUAGE: str = Field(default="en")

    # ── URL dosyası ──────────────────────────────────────────────────────────
    URLS_FILE: str = Field(
        default="urls.txt",
        description="Her satırda bir Wikipedia URL'si. "
                    "Boş veya yoksa rastgele makale modu devreye girer.",
    )

    # ── Word filtering ───────────────────────────────────────────────────────
    WORD_MIN_LENGTH: int = Field(default=5, ge=1)

    # ── Runtime ──────────────────────────────────────────────────────────────
    FETCH_INTERVAL: int = Field(default=30, ge=1)
    LOG_LEVEL: str = Field(default="INFO")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()