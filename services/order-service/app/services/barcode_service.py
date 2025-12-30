# app/services/barcode_service.py


from barcode.writer import ImageWriter
import barcode
import io
import base64
import uuid
import logging
from datetime import datetime
from typing import Optional
import aiomysql
from fastapi import HTTPException, status

from app.schemas.barcode import BarcodeCreate, BarcodeOut
from app.crud.crud_barcode import crud_barcode

logger = logging.getLogger(__name__)

class BarcodeService:
    """
    Service để tạo và quản lý barcode cho đơn hàng.
    
    - Tạo barcode duy nhất cho mỗi đơn hàng
    - Generate barcode image (Code128 format)
    - Hỗ trợ scan và tracking
    """
    
    @staticmethod
    def generate_barcode_value(order_id: str) -> str:
        """
        Tạo giá trị barcode duy nhất dựa trên order_id.
        
        Format: ORD-{8 ký tự đầu order_id}-{timestamp}
        Ví dụ: ORD-A1B2C3D4-1234567890
        
        Args:
            order_id: ID của đơn hàng
            
        Returns:
            str: Mã barcode duy nhất
        """
        short_id = order_id.replace("-", "")[:8].upper()
        timestamp = str(int(datetime.utcnow().timestamp()))[-6:]
        return f"ORD{short_id}{timestamp}"
    
    # ...existing code...

    @staticmethod
    async def create_barcode_for_order(
        db: aiomysql.Connection,
        order_id: str
    ) -> BarcodeOut:
        """Tạo barcode mới cho đơn hàng."""
        try:
            barcode_id = f"BC-{uuid.uuid4().hex[:12].upper()}"
            code_value = BarcodeService.generate_barcode_value(order_id)
            
            async with db.cursor(aiomysql.DictCursor) as cursor:
                query = """
                    INSERT INTO barcode (barcode_id, code_value, generated_at)
                    VALUES (%s, %s, %s)
                """
                generated_at = datetime.utcnow()
                await cursor.execute(query, (barcode_id, code_value, generated_at))
                
                await db.commit()
                
                # Lấy lại record vừa tạo
                await cursor.execute(
                    "SELECT * FROM barcode WHERE barcode_id = %s", 
                    (barcode_id,)
                )
                result = await cursor.fetchone()
            
            logger.info(f"Đã tạo và commit barcode {code_value} cho order {order_id}")
            return BarcodeOut.model_validate(result)
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo barcode cho order {order_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể tạo barcode: {str(e)}"
            )
    @staticmethod
    def generate_barcode_image(code_value: str) -> str:
        """
        Tạo hình ảnh barcode dạng base64.
        
        Sử dụng Code128 - format phổ biến cho logistics.
        
        Args:
            code_value: Giá trị của barcode
            
        Returns:
            str: Base64 encoded image (có thể dùng trực tiếp trong HTML/PDF)
        """
        try:
            # Tạo barcode Code128
            CODE128 = barcode.get_barcode_class('code128')
            barcode_instance = CODE128(code_value, writer=ImageWriter())
            
            # Render ra buffer
            buffer = io.BytesIO()
            barcode_instance.write(buffer, options={
                'module_width': 0.3,    # Độ rộng mỗi bar
                'module_height': 10.0,  # Chiều cao barcode
                'font_size': 10,        # Size của text dưới barcode
                'text_distance': 3,     # Khoảng cách text và barcode
                'quiet_zone': 2.5       # Margin xung quanh
            })
            
            # Convert sang base64
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo hình ảnh barcode: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể tạo hình ảnh barcode"
            )
    
    @staticmethod
    async def get_barcode_by_code(
        db: aiomysql.Connection,
        code_value: str
    ) -> Optional[BarcodeOut]:
        """
        Tìm barcode theo code_value (dùng khi scan).
        
        Args:
            db: Database connection
            code_value: Mã barcode được quét
            
        Returns:
            BarcodeOut hoặc None nếu không tìm thấy
        """
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT * FROM barcode WHERE code_value = %s"
                await cursor.execute(query, (code_value,))
                result = await cursor.fetchone()
                
                if result:
                    return BarcodeOut.model_validate(result)
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi tìm barcode {code_value}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi khi tìm kiếm barcode"
            )
    
    @staticmethod
    async def verify_barcode(
        db: aiomysql.Connection,
        code_value: str
    ) -> bool:
        """
        Kiểm tra barcode có tồn tại và hợp lệ không.
        
        Args:
            db: Database connection
            code_value: Mã barcode cần verify
            
        Returns:
            bool: True nếu barcode hợp lệ
        """
        barcode_obj = await BarcodeService.get_barcode_by_code(db, code_value)
        return barcode_obj is not None
