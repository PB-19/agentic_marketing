from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    GOOGLE_GENAI_MODEL: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str
    GOOGLE_GENAI_USE_VERTEXAI: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str
    GCS_BUCKET_NAME: str = "agentic-marketing-pages"
    TINYURL_API_KEY: str

    model_config = {"env_file": ".env"}


settings = Settings()
