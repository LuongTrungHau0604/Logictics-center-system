# app/models/order.py

from sqlalchemy import Column, String, Text, Enum, DateTime, Integer, ForeignKey, Numeric
from sqlalchemy.sql import func
from app.db.base import Base # (Hoặc import Base của bạn)
import uuid

# Định nghĩa các trạng thái
StatusEnum = Enum(
    'PENDING', 'IN_TRANSIT', 'AT_WAREHOUSE', 'DELIVERING', 
    'COMPLETED', 'CANCELLED',
    name='order_status_enum'
)

class Order(Base):
    __tablename__ = "orders"

    # --- Khóa và ID ---
    order_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # --- CẬP NHẬT 1 (orders_ibfk_1) ---
    # Tham chiếu đến bảng 'sme'
    sme_id = Column(String(50), ForeignKey("sme.sme_id"), nullable=False, index=True)
    
    # --- CẬP NHẬT 2 (orders_ibfk_4) ---
    # Tham chiếu đến bảng 'barcode'
    barcode_id = Column(String(50), ForeignKey("barcode.barcode_id"), unique=True, nullable=False)
    
    # --- Thông tin người nhận (Bắt buộc) ---
    receiver_name = Column(String(255), nullable=False)
    receiver_phone = Column(String(20), nullable=False)
    receiver_address = Column(Text, nullable=False)
    
    # --- SỬA LỖI: Dùng Numeric thay vì Decimal ---
    receiver_latitude = Column(Numeric(10, 8), nullable=False)
    receiver_longitude = Column(Numeric(11, 8), nullable=False)
    
    # --- Chi tiết gói hàng ---
    weight = Column(Numeric(10, 2), nullable=False)  # SỬA: Decimal → Numeric
    dimensions = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    
    # --- Trạng thái & Điều phối (Do service quản lý) ---
    status = Column(StatusEnum, nullable=False, default='PENDING')
    
    # --- CẬP NHẬT 3 (fk_order_to_area) ---
    # Tham chiếu đến bảng 'areas'
    area_id = Column(String(50), ForeignKey("areas.area_id"), nullable=True, index=True)
    
    # --- CẬP NHẬT 4 (fk_order_to_active_leg) ---
    # Tham chiếu đến bảng 'order_journey_leg' (Giả sử PK là 'leg_id' kiểu Integer)
    active_leg_id = Column(Integer, ForeignKey("order_journey_leg.leg_id"), nullable=True)
    
    # --- Dấu thời gian (Tự động) ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # (Bạn có thể thêm các 'relationships' ở đây nếu dùng ORM đầy đủ)