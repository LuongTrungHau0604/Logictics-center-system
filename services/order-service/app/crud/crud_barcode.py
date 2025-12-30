# app/crud/crud_barcode.py

from .base import CRUDBase
from app.models.barcode import Barcode
# Import thêm BarcodeUpdate từ schema
from app.schemas.barcode import BarcodeCreate, BarcodeUpdate 

# SỬA LỖI Ở ĐÂY: Thêm BarcodeUpdate vào
class CRUDBarcode(CRUDBase[Barcode, BarcodeCreate, BarcodeUpdate]):
    pass

crud_barcode = CRUDBarcode(Barcode)