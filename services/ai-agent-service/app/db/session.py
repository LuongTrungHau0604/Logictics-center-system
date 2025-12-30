import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings # Giả sử bạn có DATABASE_URL trong settings

logger = logging.getLogger(__name__)

# --- 1. Tạo Engine ---
# create_engine chỉ cần chạy 1 lần khi ứng dụng khởi động
try:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,  # Tự động kiểm tra kết nối
        pool_recycle=3600    # Tái sử dụng kết nối sau 1 giờ
    )
    logger.info("✅ Database engine created successfully.")
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}", exc_info=True)
    engine = None

# --- 2. Tạo SessionLocal (Nhà máy tạo session) ---
# SessionLocal là một "class" mà chúng ta sẽ dùng để tạo session mới
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# --- 3. Hàm Dependency (Quan trọng nhất) ---
def get_db():
    """
    Dependency của FastAPI: Cung cấp một session CSDL cho mỗi request.
    Đây là nơi xử lý COMMIT và ROLLBACK.
    """
    if engine is None:
        logger.error("❌ Database engine is not initialized. Cannot create session.")
        raise Exception("Database engine not initialized")
        
    db: Session = SessionLocal()
    try:
        # Giao session (db) cho endpoint sử dụng
        yield db
        
        # --- MẤU CHỐT LÀ ĐÂY ---
        # Nếu endpoint chạy xong mà KHÔNG có lỗi, commit tất cả thay đổi
        db.commit()
        
    except Exception as e:
        # Nếu có bất kỳ lỗi nào (HTTPException, lỗi CSDL, v.v.)
        logger.warning(f"🔥 Rolling back transaction due to error: {e}")
        db.rollback() # Hoàn tác tất cả db.add()
        raise e # Ném lỗi ra để FastAPI xử lý
        
    finally:
        # Luôn luôn đóng session sau khi request kết thúc
        db.close()