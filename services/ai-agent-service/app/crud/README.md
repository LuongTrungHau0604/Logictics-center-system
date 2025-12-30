# app/crud/README.md
# CRUD Operations for Logistics System

Tài liệu hướng dẫn sử dụng các CRUD functions cho hệ thống logistics.

## Cấu trúc CRUD

```
app/crud/
├── __init__.py          # Export tất cả CRUD functions
├── base.py              # Generic CRUD operations
├── crud_warehouse.py    # CRUD cho Warehouse
├── crud_sme.py          # CRUD cho SME
├── crud_order.py        # CRUD cho Order
├── crud_order_route.py  # CRUD cho OrderRoute
└── usage_example.py     # Ví dụ sử dụng
```

## Import và sử dụng

```python
from app.crud import (
    create_warehouse, get_all_active_warehouses,
    create_sme, update_sme_coordinates,
    create_order, update_order_ai_routing
)
```

## Chức năng chính

### 1. Warehouse Management
- `create_warehouse()` - Tạo kho mới
- `get_warehouse()` - Lấy thông tin kho
- `get_all_active_warehouses()` - Lấy tất cả kho đang hoạt động
- `update_warehouse()` - Cập nhật thông tin kho
- `delete_warehouse()` - Xóa kho

### 2. SME Management
- `create_sme()` - Tạo SME mới
- `get_sme()` - Lấy thông tin SME
- `update_sme_coordinates()` - Cập nhật tọa độ SME (cho geocoding)
- `get_smes_by_area()` - Lấy SME theo khu vực

### 3. Order Management
- `create_order()` - Tạo đơn hàng mới
- `get_orders_by_status()` - Lấy đơn hàng theo trạng thái
- `update_order_ai_routing()` - AI cập nhật routing cho đơn hàng
- `update_order_status()` - Cập nhật trạng thái đơn hàng

### 4. Order Route Management
- `create_order_route()` - Tạo tuyến đường
- `get_routes_by_order()` - Lấy tuyến đường theo đơn hàng
- `update_route_status()` - Cập nhật trạng thái tuyến đường

## Luồng xử lý AI

1. **Lấy đơn hàng pending**: `get_orders_by_status(db, "PENDING_PROCESSING")`
2. **Lấy kho hoạt động**: `get_all_active_warehouses(db)`
3. **AI tìm kho tối ưu**: Thuật toán tìm kho gần nhất
4. **Cập nhật đơn hàng**: `update_order_ai_routing(db, order, ai_data)`
5. **Tạo routing**: `create_order_route(db, route_data)`

## Ví dụ sử dụng

```python
# Tạo đơn hàng mới
order_data = schemas.OrderCreate(
    order_code="ORD001",
    sme_id="sme-001",
    receiver_name="Nguyễn Văn A",
    receiver_phone="0901234567",
    receiver_address="123 ABC Street"
)
order = create_order(db, order_data)

# AI cập nhật routing
ai_update = schemas.OrderUpdateByAI(
    pickup_warehouse_id="wh-001",
    destination_warehouse_id="wh-002",
    status="READY_FOR_PICKUP"
)
updated_order = update_order_ai_routing(db, order, ai_update)
```

## Schemas đặc biệt

### OrderUpdateByAI
Schema này được thiết kế riêng cho AI Agent để cập nhật thông tin warehouse routing:

```python
class OrderUpdateByAI(BaseModel):
    pickup_warehouse_id: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    status: Optional[str] = None
```

### SMEUpdateCoordinates
Schema để cập nhật tọa độ SME sau khi geocoding:

```python
class SMEUpdateCoordinates(BaseModel):
    latitude: Decimal
    longitude: Decimal
```

## Lưu ý quan trọng

1. **Session Management**: Tất cả CRUD functions nhận `db: Session` và không tự commit
2. **Error Handling**: Cần wrap trong try-catch ở tầng API
3. **AI Integration**: Sử dụng schema `OrderUpdateByAI` cho AI operations
4. **Nullable Warehouses**: Order có thể không có warehouse ban đầu, AI sẽ assign sau