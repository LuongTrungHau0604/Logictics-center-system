import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.mysql_connection import connect_to_db, close_db
from app.core.config import settings


# Import các API Routers
from app.api.v1.endpoints import auth as auth_router
from app.api.v1.endpoints import users as user_router
from app.api.v1.endpoints import sme as sme_router
from app.api.v1.endpoints import employee as employee_router
from app.api.v1.endpoints import Shipper as shipper_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CHỌN 1 TRONG 2: Lifespan HOẶC on_event (KHÔNG ĐƯỢC CẢ 2!) ---

# OPTION 1: Dùng lifespan (Recommended cho FastAPI mới)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời ứng dụng."""
    logger.info("--- 🚀 Starting application ---")
    try:
        await connect_to_db()
        logger.info("✅ Database connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Don't raise - let app start với degraded functionality
    
    yield  # App is running
    
    logger.info("--- 🔌 Shutting down application ---")
    await close_db()

app = FastAPI(
    title=settings.project_name,
    description="Authentication and User Management Service", 
    version="1.0.0",
    lifespan=lifespan  # ← Dùng lifespan
)

# CORS
origins = [
    "http://localhost:8002",
    "http://localhost:8001", 
    "http://localhost:3000",
    "http://localhost:5173",
    "*" # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn (Web, App, Mobile) truy cập
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các method (GET, POST, PUT, DELETE...)
    allow_headers=["*"],  # Cho phép tất cả các header
)

# SỬA LỖI: XÓA BỎ @app.on_event (conflict với lifespan)
# @app.on_event("startup")  # ← XÓA DÒNG NÀY
# @app.on_event("shutdown") # ← XÓA DÒNG NÀY

# Include API routes
app.include_router(
    auth_router.router, 
    prefix=f"{settings.api_v1_str}/auth",  # Kết hợp /api/v1 + /auth
    tags=["Authentication"]
)

app.include_router(
    user_router.router, 
    prefix=f"{settings.api_v1_str}/users",
    tags=["Users"]
)

app.include_router(
    sme_router.router, 
    prefix=f"{settings.api_v1_str}/sme",
    tags=["SME"]
)

app.include_router(
    employee_router.router, 
    prefix=f"{settings.api_v1_str}/employees",
    tags=["Employee"]
)

app.include_router(
    shipper_router.router,
    prefix=f"{settings.api_v1_str}/shippers",
    tags=["Shipper"]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    from app.db.mysql_connection import get_db_pool
    
    pool = get_db_pool()
    if pool is None:
        return {"status": "unhealthy", "database": "not connected"}
    
    return {
        "status": "healthy", 
        "database": "connected",
        "pool_size": pool.size,
        "pool_free": pool.freesize
    }

@app.get("/")
async def root():
    return {"message": "Identity Service is running!"}
