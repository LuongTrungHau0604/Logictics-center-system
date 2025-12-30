import aiomysql
import logging
from typing import Optional

# Import 'settings' từ file config của bạn
from app.core.config import settings

logger = logging.getLogger(__name__)

# Biến global này sẽ giữ connection pool
db_pool: Optional[aiomysql.Pool] = None


# --- THAY ĐỔI 2: Tạo hàm "getter" ---
def get_db_pool() -> Optional[aiomysql.Pool]:
    """Trả về CSDL pool hiện tại."""
    return db_pool

async def connect_to_db():
    """
    Khởi tạo connection pool khi ứng dụng FastAPI khởi động.
    """
    global db_pool
    logger.info("Đang khởi tạo MySQL connection pool...")
    try:
        db_pool = await aiomysql.create_pool(
            host=settings.DB_HOST, 
            port=settings.DB_PORT,
            user=settings.DB_USER, 
            password=settings.DB_PASSWORD,
            db=settings.DB_NAME,
            minsize=5,  # Số kết nối tối thiểu
            maxsize=20, # Số kết nối tối đa
            autocommit=False, # Rất quan trọng cho transactions
            loop=None # Tự động lấy event loop
        )
        logger.info("✅ MySQL connection pool đã khởi tạo thành công.")
    except Exception as e:
        logger.critical(f"❌ Không thể khởi tạo MySQL connection pool: {e}", exc_info=True)
        # (Bạn có thể muốn raise lỗi ở đây để dừng ứng dụng)

async def close_db():
    """
    Đóng connection pool khi ứng dụng FastAPI tắt.
    """
    global db_pool
    if db_pool:
        logger.info("Đang đóng MySQL connection pool...")
        db_pool.close()
        await db_pool.wait_closed()
        logger.info("✅ MySQL connection pool đã được đóng.")