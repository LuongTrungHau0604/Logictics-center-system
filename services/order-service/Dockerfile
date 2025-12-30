# 1. Chọn Base Image: Python 3.11 bản slim (nhẹ, khoảng 150MB)
FROM python:3.11-slim

# 2. Ngăn Python tạo ra các file .pyc (không cần thiết trong Docker)
ENV PYTHONDONTWRITEBYTECODE=1
# 3. Log sẽ được in ngay lập tức ra màn hình console (quan trọng để debug)
ENV PYTHONUNBUFFERED=1

# 4. Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# 5. Copy file thư viện vào trước (để tận dụng cache của Docker)
COPY requirements.txt .

# 6. Cài đặt thư viện
# --no-cache-dir giúp giảm dung lượng image
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copy toàn bộ code dự án vào container
COPY . .

# 8. Mở port 8001 (Port bạn dùng trong code)
EXPOSE 8001

# 9. Lệnh chạy server
# Lưu ý: host 0.0.0.0 là bắt buộc để truy cập từ ngoài container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]