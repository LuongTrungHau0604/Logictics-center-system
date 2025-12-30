# app/models/order_warehouse_log.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class OrderWarehouseLog(Base):
    """
    Bảng lưu lịch sử di chuyển của đơn hàng qua các kho.
    
    Mỗi lần nhân viên quét barcode tại kho, sẽ tạo 1 record mới.
    """
    __tablename__ = "order_warehouse_logs"

    log_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tham chiếu đến đơn hàng
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False, index=True)
    
    # Tham chiếu đến kho
    warehouse_id = Column(String(50), ForeignKey("warehouses.warehouse_id"), nullable=False, index=True)
    
    # Thông tin scan
    scanned_by = Column(String(50), nullable=True)  # User ID của nhân viên quét
    scanned_at = Column(DateTime, nullable=False, default=func.now())
    
    # Trạng thái tại thời điểm scan
    action = Column(String(50), nullable=False)  # CHECK_IN, CHECK_OUT, PROCESSING, etc.
    
    # Ghi chú (nếu có)
    note = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
