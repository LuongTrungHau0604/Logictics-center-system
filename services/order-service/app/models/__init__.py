# order-service/app/models/__init__.py

# Import Base từ file base.py để các model có thể kế thừa
from app.db.base import Base

# Import tất cả các model của bạn vào đây

from .order import Order
from .barcode import Barcode

# Dòng này khai báo những gì sẽ được export khi ai đó import `from app.models import *`
__all__ = ["Base","Order", "Barcode"]