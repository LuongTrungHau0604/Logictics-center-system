# 📦 Hướng Dẫn Sử Dụng Hệ Thống Barcode Tracking

## 🎯 Tổng Quan

Hệ thống barcode tracking cho phép theo dõi đơn hàng khi di chuyển qua các kho bằng cách:
1. **Tự động tạo barcode** khi tạo đơn hàng mới
2. **Quét barcode** tại mỗi kho để cập nhật vị trí
3. **Xem lịch sử** di chuyển của đơn hàng

---

## 🗂️ Cấu Trúc File Đã Tạo

```
services/order-service/
├── app/
│   ├── models/
│   │   ├── barcode.py                    # Model barcode
│   │   └── order_warehouse_log.py        # Model lưu lịch sử tracking ✨ MỚI
│   │
│   ├── schemas/
│   │   ├── barcode.py                    # Schema barcode
│   │   └── order_warehouse_log.py        # Schema cho tracking ✨ MỚI
│   │
│   ├── crud/
│   │   ├── crud_barcode.py               # CRUD barcode
│   │   └── crud_order_warehouse_log.py   # CRUD tracking ✨ MỚI
│   │
│   ├── services/
│   │   └── barcode_service.py            # Service tạo/quản lý barcode ✨ MỚI
│   │
│   └── api/v1/endpoints/
│       └── barcode.py                    # API endpoints ✨ MỚI
│
└── migrations/
    └── create_order_warehouse_logs.sql   # Migration script ✨ MỚI
```

---

## 🔧 Cài Đặt

### 1. Chạy Migration

```sql
-- Tạo bảng order_warehouse_logs
mysql -u root -p shipping_db < migrations/create_order_warehouse_logs.sql
```

### 2. Cài Đặt Dependencies (Đã có sẵn)

```bash
pip install python-barcode Pillow
```

---

## 🚀 Cách Sử Dụng

### 📝 **1. Tạo Đơn Hàng (Tự động tạo barcode)**

Khi tạo đơn hàng mới, barcode sẽ được tạo tự động:

```python
# Trong order_service.py hoặc endpoint tạo đơn hàng
from app.services.barcode_service import BarcodeService

# Sau khi tạo order thành công
barcode = await BarcodeService.create_barcode_for_order(
    db=db,
    order_id=created_order.order_id
)

# Barcode value: ORD12345678901234 (dạng này dễ quét)
```

---

### 📷 **2. Quét Barcode Tại Kho**

**API Endpoint:** `POST /api/v1/barcode/scan`

**Request Body:**
```json
{
  "code_value": "ORD12345678901234",
  "warehouse_id": "WH-HCM-001",
  "action": "CHECK_IN",
  "note": "Hàng đến lúc 14:30, tình trạng tốt"
}
```

**Actions:**
- `CHECK_IN`: Hàng vào kho
- `CHECK_OUT`: Hàng ra khỏi kho (chuyển tiếp)
- `PROCESSING`: Đang xử lý (phân loại, đóng gói...)

**Response:**
```json
{
  "success": true,
  "message": "Đã ghi nhận đơn hàng ORDER-ABC123 tại Kho HCM 1",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_code": "ORDER-ABC123",
  "current_warehouse": "Kho HCM 1",
  "action": "CHECK_IN",
  "log": {
    "log_id": "...",
    "order_id": "...",
    "warehouse_id": "WH-HCM-001",
    "scanned_by": "user_123",
    "scanned_at": "2025-11-14T10:30:00",
    "action": "CHECK_IN",
    "note": "..."
  }
}
```

---

### 📊 **3. Xem Lịch Sử Đơn Hàng**

**API Endpoint:** `GET /api/v1/barcode/order/{order_id}/history`

**Response:**
```json
[
  {
    "log_id": "...",
    "order_id": "...",
    "warehouse_id": "WH-HN-001",
    "scanned_by": "user_456",
    "scanned_at": "2025-11-14T16:00:00",
    "action": "CHECK_OUT",
    "note": "Chuyển đến HCM"
  },
  {
    "log_id": "...",
    "order_id": "...",
    "warehouse_id": "WH-HN-001",
    "scanned_at": "2025-11-14T10:00:00",
    "action": "CHECK_IN",
    "note": "Nhận từ SME"
  }
]
```

---

### 🖼️ **4. Lấy Hình Ảnh Barcode (Để In/Hiển Thị)**

**API Endpoint:** `GET /api/v1/barcode/{code_value}/image`

**Response:**
```json
{
  "code_value": "ORD12345678901234",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

Dùng image base64 này để:
- Hiển thị trong HTML: `<img src="{image}" />`
- In trên PDF/label
- Gửi qua email

---

### 🏭 **5. Xem Logs của Kho**

**API Endpoint:** `GET /api/v1/barcode/warehouse/{warehouse_id}/logs?limit=50`

Dùng cho nhân viên kho xem lịch sử các đơn hàng đã xử lý.

---

## 🎨 Flow Hoàn Chỉnh

```
┌─────────────────┐
│  SME tạo đơn    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Barcode tự động tạo    │
│  Format: ORD{id}{time}  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  In barcode & dán lên   │
│  kiện hàng              │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Kho HN: Quét barcode   │
│  Action: CHECK_IN       │
│  → Lưu log vào DB       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Kho HN: Xử lý xong     │
│  Action: CHECK_OUT      │
│  → Chuyển đến HCM       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Kho HCM: CHECK_IN      │
│  → Lưu log              │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Khách hàng/SME xem     │
│  lịch sử di chuyển      │
│  qua API history        │
└─────────────────────────┘
```

---

## 📱 Ví Dụ Tích Hợp Frontend

### React/Next.js - Quét Barcode

```typescript
// Component: BarcodeScannerPage.tsx
import { useState } from 'react';

function BarcodeScannerPage() {
  const [scannedCode, setScannedCode] = useState('');
  
  const handleScan = async () => {
    const response = await fetch('/api/v1/barcode/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code_value: scannedCode,
        warehouse_id: 'WH-HCM-001',
        action: 'CHECK_IN',
        note: 'Scan qua mobile app'
      })
    });
    
    const result = await response.json();
    alert(result.message);
  };
  
  return (
    <div>
      <input 
        type="text" 
        value={scannedCode}
        onChange={(e) => setScannedCode(e.target.value)}
        placeholder="Quét hoặc nhập barcode"
      />
      <button onClick={handleScan}>Xác Nhận</button>
    </div>
  );
}
```

### Mobile App - Sử dụng Camera

Bạn có thể tích hợp thư viện:
- **React Native:** `react-native-camera`
- **Flutter:** `mobile_scanner`
- **Ionic:** `@capacitor/barcode-scanner`

---

## 🔐 Bảo Mật

- ✅ Endpoint `/barcode/scan` yêu cầu authentication (JWT token)
- ✅ Chỉ nhân viên có quyền mới quét được
- ✅ Log ghi lại `scanned_by` để audit trail

---

## 📈 Tối Ưu Hóa

### Index Database
Đã tạo sẵn indexes cho:
- `order_id` (tra cứu lịch sử đơn hàng)
- `warehouse_id` (tra cứu logs của kho)
- `scanned_at` (sắp xếp theo thời gian)

### Performance Tips
- Dùng pagination khi query logs (`LIMIT`, `OFFSET`)
- Cache barcode image nếu cần in nhiều lần
- Có thể lưu barcode image vào S3/CDN thay vì generate mỗi lần

---

## 🐛 Xử Lý Lỗi Thường Gặp

| Lỗi | Nguyên Nhân | Giải Pháp |
|------|-------------|-----------|
| `Barcode không tồn tại` | Quét sai mã | Kiểm tra lại barcode |
| `Không tìm thấy đơn hàng` | Barcode chưa được gán cho order | Kiểm tra DB |
| `Kho không tồn tại` | warehouse_id sai | Kiểm tra danh sách kho |

---

## 🎯 Mở Rộng Trong Tương Lai

- [ ] Hỗ trợ QR Code (ngoài barcode thông thường)
- [ ] Push notification khi đơn hàng đến kho mới
- [ ] Dashboard real-time tracking
- [ ] Export lịch sử ra Excel/PDF
- [ ] Tích hợp với máy scan barcode chuyên dụng

---

## 📞 Liên Hệ & Hỗ Trợ

Nếu có thắc mắc, vui lòng tạo issue hoặc liên hệ team dev.

**Happy Tracking! 🚀**
