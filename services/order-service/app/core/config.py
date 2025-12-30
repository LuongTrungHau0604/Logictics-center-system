# Config management for .env
# services/order-service/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Project settings
    PROJECT_NAME: str = "Order Service"
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api/v1"
    PORT: int = 8001  # Order Service port
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 3307
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "shipping_center_system"
    
    # Security (SHARED với identity-service để decode JWT nếu cần)
    SECRET_KEY: str = "your_very_long_secret_key_at_least_32_characters_long_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    SMTP_SERVER: str
    SMTP_PORT: int
    SENDER_EMAIL: str
    SENDER_PASSWORD: str
    
    # SỬA LỖI: Thêm URL của Identity Service
    IDENTITY_SERVICE_URL: str = "http://localhost:8000/api/v1"
    AI_AGENT_SERVICE_URL: str = "http://localhost:8002/api/v1"
    
    @property
    def database_url(self) -> str:
        password_encoded = quote_plus(self.DB_PASSWORD)
        return f"mysql+aiomysql://{self.DB_USER}:{password_encoded}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()