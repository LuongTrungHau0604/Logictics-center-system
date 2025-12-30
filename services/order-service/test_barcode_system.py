# test_barcode_system.py
# Script demo để test hệ thống barcode tracking

import requests
import json

# === CONFIG ===
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token_here"  # Thay bằng token thật

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === 1. TẠO ĐỌN HÀNG MỚI (tự động tạo barcode) ===
print("=" * 60)
print("1. TẠO ĐƠN HÀNG MỚI")
print("=" * 60)

order_data = {
    "receiver_name": "Nguyễn Văn A",
    "receiver_phone": "0901234567",
    "receiver_address": "123 Lê Lợi, Quận 1, TP.HCM",
    "weight": 2.5,
    "dimensions": "30x20x15",
    "note": "Hàng dễ vỡ"
}

response = requests.post(
    f"{BASE_URL}/orders",
    headers=headers,
    json=order_data
)

if response.status_code == 200:
    order = response.json()
    print(f"✅ Tạo đơn hàng thành công!")
    print(f"   Order ID: {order['order_id']}")
    print(f"   Order Code: {order['order_code']}")
    
    # Lấy barcode
    barcode_response = requests.get(
        f"{BASE_URL}/orders/{order['order_id']}/barcode",
        headers=headers
    )
    
    if barcode_response.status_code == 200:
        barcode = barcode_response.json()
        print(f"   Barcode: {barcode['code_value']}")
        print(f"\n   📱 Quét mã này: {barcode['code_value']}")
        
        # Lưu lại để test
        BARCODE_VALUE = barcode['code_value']
        ORDER_ID = order['order_id']
else:
    print(f"❌ Lỗi: {response.json()}")
    exit()

# === 2. QUÉT BARCODE TẠI KHO HÀ NỘI ===
print("\n" + "=" * 60)
print("2. QUÉT BARCODE TẠI KHO HÀ NỘI (CHECK_IN)")
print("=" * 60)

scan_data = {
    "code_value": BARCODE_VALUE,
    "warehouse_id": "WH-HN-001",
    "action": "CHECK_IN",
    "note": "Nhận hàng lúc 10:00, tình trạng tốt"
}

response = requests.post(
    f"{BASE_URL}/barcode/scan",
    headers=headers,
    json=scan_data
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ {result['message']}")
    print(f"   Kho: {result['current_warehouse']}")
    print(f"   Action: {result['action']}")
    print(f"   Scanned at: {result['log']['scanned_at']}")
else:
    print(f"❌ Lỗi: {response.json()}")

# === 3. XỬ LÝ XONG & XUẤT KHO ===
print("\n" + "=" * 60)
print("3. QUÉT BARCODE - XUẤT KHO HÀ NỘI (CHECK_OUT)")
print("=" * 60)

scan_data = {
    "code_value": BARCODE_VALUE,
    "warehouse_id": "WH-HN-001",
    "action": "CHECK_OUT",
    "note": "Chuyển đến HCM lúc 14:00"
}

response = requests.post(
    f"{BASE_URL}/barcode/scan",
    headers=headers,
    json=scan_data
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ {result['message']}")
else:
    print(f"❌ Lỗi: {response.json()}")

# === 4. NHẬP KHO HỒ CHÍ MINH ===
print("\n" + "=" * 60)
print("4. QUÉT BARCODE TẠI KHO HCM (CHECK_IN)")
print("=" * 60)

scan_data = {
    "code_value": BARCODE_VALUE,
    "warehouse_id": "WH-HCM-001",
    "action": "CHECK_IN",
    "note": "Hàng về kho HCM lúc 18:00"
}

response = requests.post(
    f"{BASE_URL}/barcode/scan",
    headers=headers,
    json=scan_data
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ {result['message']}")
else:
    print(f"❌ Lỗi: {response.json()}")

# === 5. XEM LỊCH SỬ DI CHUYỂN ===
print("\n" + "=" * 60)
print("5. XEM LỊCH SỬ DI CHUYỂN ĐƠN HÀNG")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/barcode/order/{ORDER_ID}/history",
    headers=headers
)

if response.status_code == 200:
    history = response.json()
    print(f"\n📦 Đơn hàng đã đi qua {len(history)} điểm:")
    print("\n" + "-" * 60)
    
    for i, log in enumerate(reversed(history), 1):
        print(f"{i}. {log['scanned_at']}")
        print(f"   Kho: {log['warehouse_id']}")
        print(f"   Action: {log['action']}")
        print(f"   Note: {log['note'] or 'N/A'}")
        print("-" * 60)
else:
    print(f"❌ Lỗi: {response.json()}")

# === 6. LẤY HÌNH ẢNH BARCODE ===
print("\n" + "=" * 60)
print("6. LẤY HÌNH ẢNH BARCODE")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/barcode/{BARCODE_VALUE}/image",
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Đã tạo hình ảnh barcode")
    print(f"   Code: {result['code_value']}")
    print(f"   Image (base64): {result['image'][:50]}...")
    print(f"\n   💡 Sử dụng trong HTML:")
    print(f'   <img src="{result["image"]}" />')
else:
    print(f"❌ Lỗi: {response.json()}")

print("\n" + "=" * 60)
print("✨ HOÀN TẤT TEST!")
print("=" * 60)
