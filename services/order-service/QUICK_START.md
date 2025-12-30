# 🚀 Quick Start - Barcode Tracking System

## 📋 Bước 1: Setup Database (1 phút)

```bash
# Chạy migration
mysql -u root -p shipping_db < migrations/create_order_warehouse_logs.sql
```

---

## 📦 Bước 2: Tạo Đơn Hàng (Barcode Tự Động)

**Endpoint:** `POST /api/v1/orders/create`

```json
{
  "receiver_name": "Nguyễn Văn A",
  "receiver_phone": "0901234567",
  "receiver_address": "123 Lê Lợi, Quận 1, TP.HCM",
  "weight": 2.5,
  "note": "Hàng dễ vỡ"
}
```

**Response:**
```json
{
  "order_id": "abc-123-...",
  "order_code": "ORDER-ABC123",
  "barcode_id": "BC-XYZ456"
  ...
}
```

---

## 🔍 Bước 3: Lấy Barcode

**Endpoint:** `GET /api/v1/orders/{order_id}/barcode`

**Response:**
```json
{
  "barcode_id": "BC-XYZ456",
  "code_value": "ORD12345678901234",  // ← Quét mã này
  "generated_at": "2025-11-14T10:00:00"
}
```

---

## 📱 Bước 4: Quét Barcode Tại Kho

**Endpoint:** `POST /api/v1/barcode/scan`

```json
{
  "code_value": "ORD12345678901234",
  "warehouse_id": "WH-HCM-001",
  "action": "CHECK_IN",
  "note": "Nhận hàng lúc 10:00"
}
```

**Actions:**
- `CHECK_IN` - Hàng vào kho
- `CHECK_OUT` - Hàng ra kho
- `PROCESSING` - Đang xử lý

---

## 📊 Bước 5: Xem Lịch Sử

**Endpoint:** `GET /api/v1/barcode/order/{order_id}/history`

**Response:**
```json
[
  {
    "log_id": "...",
    "warehouse_id": "WH-HCM-001",
    "action": "CHECK_IN",
    "scanned_at": "2025-11-14T10:00:00",
    "note": "Nhận hàng lúc 10:00"
  },
  ...
]
```

---

## 🖼️ Bonus: Lấy Hình Ảnh Barcode

**Endpoint:** `GET /api/v1/barcode/{code_value}/image`

**Response:**
```json
{
  "code_value": "ORD12345678901234",
  "image": "data:image/png;base64,iVBORw0KGgo..."
}
```

**Sử dụng:**
```html
<img src="data:image/png;base64,iVBORw0KGgo..." />
```

---

## 🎯 Flow Đơn Giản

```
Tạo đơn → Lấy barcode → Quét tại kho 1 → Quét tại kho 2 → Xem lịch sử
```

---

## 📞 Cần Giúp?

Xem chi tiết: `BARCODE_TRACKING_GUIDE.md`

Test script: `python test_barcode_system.py`

---

**That's it! 🎉**
