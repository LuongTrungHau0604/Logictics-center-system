# FastAPI app entry point
# order-service/app/main.py

from fastapi import FastAPI, Depends
from app.db.mysql_connection import connect_to_db, close_db
from app.api.v1.endpoints import order
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.core.firebase import init_firebase
from app.api.v1 import deps
from app.api.v1.endpoints import scan # Import file vừa tạo
from app.api.v1.endpoints import journey
from app.api.v1.endpoints import public
from app.api.v1.endpoints import barcode
import logging
import sys


logging.basicConfig(
    level=logging.INFO, # Hoặc logging.DEBUG để xem chi tiết hơn
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

origins = [
    "http://localhost:8002", # Cho phép Order-Service Swagger
    "http://localhost:3000", # (Nếu FE React của bạn chạy ở port 3000)
    "http://localhost:8000",
    "http://localhost:8001", # Cho phép SME-Service Swagger
    "http://localhost:5173",  # Thêm Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả nguồn (Web, App, Mobile) truy cập
    allow_credentials=True,
    allow_methods=["*"], # Cho phép tất cả methods (GET, POST, v.v.)
    allow_headers=["*"], # Cho phép tất cả headers
)

# SỬA LỖI: Include router với prefix đúng
app.include_router(
    order.router, 
    prefix=settings.API_PREFIX,  # "/api/v1"
    tags=["orders"],
    dependencies=[Depends(deps.get_current_user)]
)
app.include_router(
    scan.router,
    prefix=settings.API_PREFIX,  # "/api/v1"
    tags=["scan"],
    dependencies=[Depends(deps.get_current_user)]
)

app.include_router(
    journey.router,
    prefix=settings.API_PREFIX,  # "/api/v1"
    tags=["journey"],
    dependencies=[Depends(deps.get_current_user)]
)

app.include_router(
    public.router,
    prefix=settings.API_PREFIX,  # "/api/v1"
    tags=["public-tracking"]
)
app.include_router(
    barcode.router,
    prefix=settings.API_PREFIX,  # "/api/v1"
    tags=["barcodes"]
)
@app.on_event("startup")
async def startup_event():
    """
    Event được chạy khi FastAPI app start up
    """
    init_firebase()
    print("🚀 Order Service is starting up...")
    await connect_to_db()
    print("✅ Order Service startup completed!")

@app.on_event("shutdown") 
async def shutdown_event():
    """
    Event được chạy khi FastAPI app shutdown
    """
    print("🛑 Order Service is shutting down...")
    await close_db()
    print("✅ Order Service shutdown completed!")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# SỬA LỖI: Thêm health endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "order-service"}