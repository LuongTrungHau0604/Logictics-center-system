# order-service/app/crud/__init__.py

# Import các instance CRUD của bạn vào đây
from .crud_order import crud_order
from .crud_barcode import crud_barcode

# (Không bắt buộc) Khai báo để có thể dùng `from app.crud import *`
__all__ = ["crud_order", "crud_barcode"]