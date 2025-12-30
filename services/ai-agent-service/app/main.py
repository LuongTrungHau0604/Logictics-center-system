from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from app.api.v1.endpoints.scheduler_service import run_system_wide_optimization
# Import router tổng từ file api.py
from app.api.v1.api import api_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
# Initialize FastAPI app

origins = [
    "http://localhost:3001",  # Frontend React của bạn
    "http://localhost:3000",  # Frontend dự phòng (nếu có)
    "*"                       # Hoặc để dấu * để cho phép tất cả (chỉ dùng khi Dev)
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP EVENT ---
    print("🚀 System Starting... Initializing AI Scheduler...")
    
    # Thêm job: Chạy mỗi 5 phút (300 giây)
    # replace_existing=True để tránh trùng lặp job khi reload code
    scheduler.add_job(
        run_system_wide_optimization, 
        trigger=IntervalTrigger(seconds=600), 
        id="ai_auto_pilot",
        replace_existing=True
    )
    
    scheduler.start()
    
    yield # Ứng dụng chạy tại đây
    
    # --- SHUTDOWN EVENT ---
    print("🛑 System Shutting down... Stopping Scheduler...")
    scheduler.shutdown()
    
app = FastAPI(
    title="Logistics Full System",
    description="Hệ thống logistics bao gồm Agent, Warehouse và các dịch vụ khác.",
    version="1.0.0",
    lifespan=lifespan  # <--- BẮT BUỘC PHẢI CÓ DÒNG NÀY
)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gắn router tổng vào app ---
# Tất cả các route trong api_router sẽ có tiền tố /api/v1
app.include_router(api_router, prefix="/api/v1")


# --- Các endpoint gốc (Health Check) ---
# Những cái này thuộc về App chính, không thuộc router nào
@app.get("/")
async def root():
    """Health check endpoint cơ bản"""
    return {"message": "Logistics Full System is running"}

@app.get("/health")
async def health_check():
    """Health check chi tiết"""
    return {
        "status": "healthy",
        "service": "Logistics Full System",
        "version": "1.0.0"
    }

# Chạy server nếu file được execute trực tiếp
if __name__ == "__main__":
    import uvicorn
    # Lưu ý: uvicorn sẽ chạy 'app' từ file 'app.main'
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True, lifespan="app.main:lifespan")