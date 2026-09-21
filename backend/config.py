from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LLM_PROVIDER: str = "mock"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "prompt-generator"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "chrome-extension://*",
    ]


settings = Settings()
