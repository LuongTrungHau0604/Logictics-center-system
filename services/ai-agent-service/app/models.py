
import enum
from datetime import datetime
from typing import List, Optional
import uuid
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy import (
    Column, Integer, String, Text, Float, Enum as EnumType, 
    DateTime, ForeignKey, func, Boolean,
    Numeric, Date # Import Numeric (đã đúng)
)

# Import hàm func (cần cho server_default)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
# --- Base Model ---
Base = declarative_base()

# --- SỬA LỖI 2: Định nghĩa ENUMs ở đây (thay vì import từ chính nó) ---

class SMEStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    
class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SME = "sme"
    SHIPPER = "shipper"

class EmployeeStatus(enum.Enum): # <-- SỬA LỖI 3: Thêm Enum mới
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class SMEStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    AT_WAREHOUSE = "AT_WAREHOUSE"
    DELIVERING = "DELIVERING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class LegStatus(str, enum.Enum):
    PENDING = "PENDING"
    
    # --- THÊM DÒNG NÀY ---
    IN_PROGRESS = "IN_PROGRESS" 
    
    COMPLETED = "COMPLETED"
    
    
    CANCELLED = "CANCELLED"

class LegType(enum.Enum):
    PICKUP = "PICKUP"
    TRANSFER = "TRANSFER"
    DELIVERY = "DELIVERY"

class AreaType(enum.Enum):
    CITY = "CITY"
    DISTRICT = "DISTRICT"
    REGION = "REGION"
    CUSTOM = "CUSTOM"

class AreaStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class WarehouseType(enum.Enum):
    HUB = "HUB"
    SATELLITE = "SATELLITE"
    LOCAL_DEPOT = "LOCAL_DEPOT"

class WarehouseStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

class VehicleType(enum.Enum):
    MOTORBIKE = "MOTORBIKE"
    CAR = "CAR"
    TRUCK = "TRUCK"
    BICYCLE = "BICYCLE"

class ShipperStatus(enum.Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    DELIVERING = "DELIVERING"
# --- (Kết thúc ENUMs) ---


# --- Bảng 'user' ---
class User(Base):
    __tablename__ = "user"

    # --- Cấu trúc cột khớp với DB ---
    user_id = Column(String(30), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # SỬA: Đổi tên từ hashed_password
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    
    # DB là varchar(50), nên dùng native_enum=False
    role = Column(EnumType(UserRole, native_enum=False), nullable=False) 
    
    # THÊM: Foreign Key trỏ đến SME
    sme_id = Column(String(50), ForeignKey("sme.sme_id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # XÓA: full_name, is_active, updated_at

    # --- Quan hệ ---
    # THÊM: Một User thuộc về một SME
    sme = relationship("SME", back_populates="users")

    
class Employee(Base):
    __tablename__ = "employees"

    # Khóa chính
    employee_id = Column(String(50), primary_key=True)
    
    # Thông tin cơ bản
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    email = Column(String(255), unique=True, nullable=False)
    
    # --- 🆕 BỔ SUNG KHỚP SCHEMA ---
    dob = Column(Date, nullable=True)  # Ngày sinh
    
    # Vai trò & Trạng thái
    role = Column(EnumType(UserRole), nullable=False, default=UserRole.SHIPPER)
    status = Column(EnumType(EmployeeStatus), nullable=False, default=EmployeeStatus.ACTIVE)
    
    # --- 🔗 KHÓA NGOẠI ---
    # Schema user_id là varchar(30)
    user_id = Column(String(30), ForeignKey("user.user_id"), nullable=True) 
    
    # --- 🔥 QUAN TRỌNG: Cột này cần thiết cho logic tìm xe tải ở Hub ---
    warehouse_id = Column(String(50), ForeignKey("warehouses.warehouse_id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # --- RELATIONSHIPS ---
    # Quan hệ 1-1 với Shipper
    shipper = relationship("Shipper", back_populates="employee", uselist=False)
    
    # (Tùy chọn) Quan hệ với Warehouse để truy vấn ngược dễ hơn
    # warehouse = relationship("Warehouse", back_populates="employees")

# --- Bảng 'sme' ---
class SME(Base):
    __tablename__ = "sme"

    # --- Cấu trúc cột khớp với DB ---
    sme_id = Column(String(50), primary_key=True)
    business_name = Column(String(255), nullable=False)
    tax_code = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    # --- THAY ĐỔI QUAN TRỌNG: Tách Coordinates ---
    # Xóa cột coordinates = Column(Geometry...) cũ
    # Thêm 2 cột số thực khớp với câu lệnh ALTER TABLE
    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    
    # Thêm area_id (vì logic Order Service có lấy cột này)
    area_id = Column(String(50), nullable=True)
    
    contact_phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Status Enum
    status = Column(
        EnumType(SMEStatus, native_enum=True), 
        nullable=False, 
        default=SMEStatus.PENDING
    )
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # --- Quan hệ ---
    users = relationship("User", back_populates="sme")
    orders = relationship("Order", back_populates="sme")

# --- Bảng 'areas' ---
class Area(Base):
    __tablename__ = "areas"
    
    area_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(EnumType(AreaType), default=AreaType.CUSTOM)
    status = Column(EnumType(AreaStatus), default=AreaStatus.ACTIVE)
    
    
    center_latitude = Column(DECIMAL(10, 8))
    center_longitude = Column(DECIMAL(11, 8))
    
    radius_km = Column(Numeric(6, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    warehouses = relationship("Warehouse", back_populates="area")
    shippers = relationship("Shipper", back_populates="area")

# --- Bảng 'warehouses' ---
class Warehouse(Base):
    __tablename__ = "warehouses"
    
    warehouse_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    type = Column(EnumType(WarehouseType), default=WarehouseType.LOCAL_DEPOT)
    capacity_limit = Column(Integer, default=0)
    current_load = Column(Integer, default=0)
    
    area_id = Column(String(50), ForeignKey("areas.area_id"), nullable=True)
    

    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))

    status = Column(EnumType(WarehouseStatus), default=WarehouseStatus.ACTIVE)
    contact_phone = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="warehouses")
    origin_legs = relationship(
        "OrderJourneyLeg", 
        back_populates="origin_warehouse", 
        foreign_keys="OrderJourneyLeg.origin_warehouse_id"
    )
    destination_legs = relationship(
        "OrderJourneyLeg", 
        back_populates="destination_warehouse", 
        foreign_keys="OrderJourneyLeg.destination_warehouse_id"
    )

# --- Bảng 'shippers' ---
class Shipper(Base):
    __tablename__ = "shippers"
    
    shipper_id = Column(String(50), primary_key=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), unique=True)
    
    # (Đã XÓA 'name' và 'phone' - dùng quan hệ employee để lấy)
    
    vehicle_type = Column(EnumType(VehicleType), default=VehicleType.MOTORBIKE)
    status = Column(EnumType(ShipperStatus), default=ShipperStatus.OFFLINE)
    area_id = Column(String(50), ForeignKey("areas.area_id"), nullable=True)
    
    rating = Column(Numeric(3, 2), default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # =================================================================
    # 🆕 CÁC CỘT MỚI (Real-time Tracking & Notification)
    # =================================================================
    fcm_token = Column(String(500), nullable=True)
    
    # Dùng Numeric(10, 8) để khớp với decimal(10,8) trong MySQL
    # Giúp lưu tọa độ GPS chính xác cao
    current_latitude = Column(Numeric(10, 8), nullable=True)
    current_longitude = Column(Numeric(11, 8), nullable=True)
    
    last_location_update = Column(DateTime, nullable=True)
    
    # =================================================================
    # QUAN HỆ (RELATIONSHIPS)
    # =================================================================
    employee = relationship("Employee", back_populates="shipper")
    area = relationship("Area", back_populates="shippers")
    journey_legs = relationship("OrderJourneyLeg", back_populates="shipper")

# --- Bảng 'orders' ---
# ...existing code...

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String(50), primary_key=True)
    order_code = Column(String(100), unique=True, nullable=False)
    sme_id = Column(String(50), ForeignKey("sme.sme_id"), nullable=False) # Đã sửa (sme.sme_id)
    area_id = Column(String(50), ForeignKey("areas.area_id"), nullable=True)
    
    receiver_name = Column(String(255), nullable=False)
    receiver_phone = Column(String(20), nullable=False)
    receiver_address = Column(Text, nullable=False)
    receiver_latitude = Column(Numeric(10, 8), nullable=True)
    receiver_longitude = Column(Numeric(11, 8), nullable=True)
    
    weight = Column(Numeric(5, 2), nullable=False)
    dimensions = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    
    status = Column(EnumType(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    barcode_id = Column(String(50), ForeignKey("barcode.barcode_id"), nullable=False)
    
    
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- RELATIONSHIPS ---
    
    sme = relationship("SME", back_populates="orders")
    area = relationship("Area") # (Giả định Area có back_populates="orders")
    barcode = relationship("Barcode") # (Giả định Barcode có back_populates="order")
    
    
    # 1. Mối quan hệ cho TẤT CẢ các chặng (Đã sửa đúng)
    all_legs = relationship(
        "OrderJourneyLeg",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderJourneyLeg.sequence",
        # 🔥 PHỤC HỒI DÒNG NÀY:
        foreign_keys="[OrderJourneyLeg.order_id]" 
    )

    

# ...existing code...

# --- Bảng 'order_journey_leg' ---
# app/models/order_journey_leg.py (hoặc trong models/__init__.py)
class OrderJourneyLeg(Base):
    __tablename__ = "order_journey_legs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # --- Khóa ngoại ---
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False)
    assigned_shipper_id = Column(String(50), ForeignKey("shippers.shipper_id"), nullable=False)
    
    # --- CÁC CỘT CŨ (Giữ nguyên) ---
    origin_warehouse_id = Column(String(50), ForeignKey("warehouses.warehouse_id"), nullable=True)
    destination_warehouse_id = Column(String(50), ForeignKey("warehouses.warehouse_id"), nullable=True)
    
    # --- 🔥 SỬA ĐỔI 1: THÊM CÁC CỘT MỚI (ĐỂ KHỚP VỚI ALTER TABLE) ---
    origin_sme_id = Column(String(50), ForeignKey("sme.sme_id"), nullable=True)
    destination_is_receiver = Column(Boolean, nullable=False, default=False)
    # -----------------------------------------------------------
    
    sequence = Column(Integer, nullable=False, default=1)
    leg_type = Column(EnumType(LegType), nullable=False, default=LegType.PICKUP)
    status = Column(EnumType(LegStatus), nullable=False, default=LegStatus.PENDING)
    
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estimated_distance = Column(Numeric(8, 2), nullable=True) # (Lưu khoảng cách, ví dụ: 123456.78 km)
    
    # --- Relationships ---
    order = relationship(
        "Order", 
        back_populates="all_legs",
        foreign_keys=[order_id]
    )
    
    shipper = relationship("Shipper", back_populates="journey_legs")

    origin_warehouse = relationship(
        "Warehouse", 
        back_populates="origin_legs",
        foreign_keys=[origin_warehouse_id]
    )
    destination_warehouse = relationship(   
        "Warehouse", 
        back_populates="destination_legs",
        foreign_keys=[destination_warehouse_id]
    )
    
    # --- 🔥 SỬA ĐỔI 2: THÊM RELATIONSHIP CHO SME (Tùy chọn nhưng nên có) ---
    origin_sme = relationship(
        "SME",
        # (Để hoàn chỉnh, bạn nên thêm "origin_legs = relationship(...)" 
        #  vào model SME, back_populates="origin_sme")
        foreign_keys=[origin_sme_id]
    )

    
# --- SỬA LỖI 1: Xóa class Pydantic này ra khỏi file models ---
# class Coordinates(BaseModel):
#     latitude: float = Field(..., description="Vĩ độ (ví dụ: 10.77)")
#     longitude: float = Field(..., description="Kinh độ (ví dụ: 106.70)")
class Barcode(Base):
    __tablename__ = "barcode"
    
    barcode_id = Column(String(50), primary_key=True)
    code_value = Column(String(100), unique=True, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="barcode")