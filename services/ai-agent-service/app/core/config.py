import os
from pydantic_settings import BaseSettings
from pydantic import computed_field 
from typing import Optional
from urllib.parse import quote_plus 

class Settings(BaseSettings):
    """
    Lớp Cấu hình, tự động đọc các biến từ file .env
    """
    
    # =========================================================
    # 1. CẤU HÌNH DATABASE
    # =========================================================
    DB_HOST: str = "localhost"
    DB_PORT: int = 3307
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "logistics_db"
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Tự động tạo chuỗi kết nối CSDL từ các biến thành phần.
        """
        safe_password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{safe_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # =========================================================
    # 2. CẤU HÌNH API KEYS & AI MODELS
    # =========================================================
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"
    GOONG_API_KEY: str = ""
    ORS_API_KEY: str = ""
    GROQ_API_KEY: str = "" 
    OPENAI_API_KEY: str = "" 
    DEEPSEEK_API_KEY: str = ""

    # =========================================================
    # 3. CẤU HÌNH FIREBASE (MỚI THÊM)
    # =========================================================
    # Đường dẫn đến file JSON tải từ Firebase Console
    # Mặc định sẽ tìm file 'firebase-adminsdk.json' cùng cấp với thư mục chạy app
    FIREBASE_CREDENTIALS_PATH: str = "firebase-adminsdk.json"

    # =========================================================
    # 4. CẤU HÌNH SERVER & KHÁC
    # =========================================================
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent Service"
    VERSION: str = "1.0.0"
    
    # Cấu hình CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Cấu hình Logging
    LOG_LEVEL: str = "INFO"
    
    # Cấu hình Geocoding (Nominatim)
    NOMINATIM_USER_AGENT: str = "MyLogisticsApp/1.0"
    NOMINATIM_RATE_LIMIT: float = 1.0 
    
    # Cấu hình Logic Nghiệp vụ
    MAX_BATCH_GEOCODING: int = 50
    DEFAULT_SEARCH_RADIUS_KM: float = 10.0

    class Config:
        # Chỉ định file .env
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Bỏ qua các biến thừa trong .env mà không gây lỗi
        extra = "ignore"

# Tạo instance global của settings
settings = Settings()