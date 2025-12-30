# AI Agent Service - Setup & Run Guide

## 🚀 Hướng dẫn chạy AI Agent Service

### 1. Cài đặt Dependencies

```bash
# Chuyển đến thư mục service
cd services/ai-agent-service

# Cài đặt requirements
pip install -r requirements.txt
```

### 2. Cấu hình Environment

```bash
# Copy file env mẫu
copy .env.example .env

# Chỉnh sửa file .env với thông tin database thực tế
# DATABASE_URL=mysql+pymysql://your_username:your_password@localhost/your_database
```

### 3. Chạy ứng dụng

#### Cách 1: Chạy trực tiếp với Python
```bash
python -m app.main
```

#### Cách 2: Chạy với Uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Cách 3: Chạy với cấu hình custom
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8080 --log-level info
```

### 4. Kiểm tra ứng dụng

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

### 5. Test các endpoints

#### Geocoding Service:
```bash
# Test geocoding
curl -X POST "http://localhost:8000/api/v1/geocoding/geocode" \
  -H "Content-Type: application/json" \
  -d '{"address": "Quận 1, Thành phố Hồ Chí Minh"}'

# Test endpoint
curl http://localhost:8000/api/v1/geocoding/test
```

#### Warehouse Service:
```bash
# Test warehouse service
curl http://localhost:8000/api/v1/warehouse/test

# Find nearest warehouse
curl -X POST "http://localhost:8000/api/v1/warehouse/find-nearest" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 10.7769, "longitude": 106.7009}'
```

### 6. Cấu trúc API Endpoints

```
/api/v1/
├── geocoding/
│   ├── /geocode                 # POST - Geocode địa chỉ
│   ├── /geocode/batch          # POST - Batch geocoding
│   ├── /validate               # POST - Validate tọa độ
│   └── /test                   # GET - Test service
├── warehouse/
│   ├── /find-nearest           # POST - Tìm kho gần nhất
│   ├── /find-in-radius         # POST - Tìm kho trong bán kính
│   ├── /capacity/{id}          # GET - Thông tin capacity
│   ├── /check-availability     # POST - Kiểm tra availability
│   ├── /calculate-distance     # POST - Tính khoảng cách
│   └── /test                   # GET - Test service
├── optimization/               # Placeholder endpoints
├── ai-insights/               # Placeholder endpoints
└── order-processing/          # Placeholder endpoints
```

### 7. Development Commands

```bash
# Install development dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Format code
pip install black
black app/

# Type checking
pip install mypy
mypy app/
```

### 8. Production Deployment

```bash
# Install gunicorn for production
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 9. Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `LOG_LEVEL` | Logging level | INFO |
| `NOMINATIM_USER_AGENT` | User agent for geocoding | MyLogisticsApp/1.0 |
| `NOMINATIM_RATE_LIMIT` | Rate limit for geocoding (seconds) | 1.0 |

### 10. Troubleshooting

#### Common Issues:

1. **Import Errors**: Đảm bảo đã cài đặt tất cả dependencies
2. **Database Connection**: Kiểm tra DATABASE_URL trong .env
3. **Port Already Used**: Thay đổi port với `--port 8001`
4. **Rate Limiting**: Geocoding service có rate limit 1s/request

#### Logs:
Logs sẽ hiển thị trong console với format:
```
2025-11-03 10:00:00 - app.main - INFO - Application started
```