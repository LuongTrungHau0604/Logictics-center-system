from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Project settings
    project_name: str = "Identity Service"
    environment: str = "development"
    debug: bool = False
    ORS_API_KEY: Optional[str] = None
    # Database settings - khớp với tên trong .env file
    db_host: str = "localhost"
    db_port: int = 3307
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "identity_db"
    
    # Auth settings
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API settings
    api_v1_str: str = "/api/v1"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Compatibility properties cho code cũ
    @property
    def database_host(self) -> str:
        return self.db_host
    
    @property
    def database_port(self) -> int:
        return self.db_port
    
    @property
    def database_user(self) -> str:
        return self.db_user
    
    @property
    def database_password(self) -> str:
        return self.db_password
    
    @property
    def database_name(self) -> str:
        return self.db_name

settings = Settings()

# Debug print
if settings.debug:
    print(f"🔧 Project: {settings.project_name}")
    print(f"🔧 Environment: {settings.environment}")
    print(f"🔧 Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")