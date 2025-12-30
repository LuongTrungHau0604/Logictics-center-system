# order-service/app/crud/crud_user.py

import aiomysql
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CRUDUser:
    """
    LƯU Ý QUAN TRỌNG VỀ KIẾN TRÚC MICROSERVICE:

    File này (crud_user.py) trong `order-service` CÓ CHỦ ĐÍCH 
    để trống hoặc rất tối giản.

    Lý do:
    1.  'order-service' KHÔNG sở hữu dữ liệu người dùng (users).
    2.  'identity-service' là service duy nhất chịu trách nhiệm
        quản lý (CRUD) bảng 'users'.
    3.  'order-service' lấy thông tin người dùng (như user_id, 
        sme_id, role) trực tiếp từ JWT Token (đã được 
        'identity-service' ký).
    4.  Dependency `get_current_user` trong `app/api/deps.py` 
        sẽ giải mã token và tạo một đối tượng User "ảo"
        mà không cần truy vấn CSDL.

    Vì vậy, chúng ta không cần các hàm như `get_by_username` 
    hay `create_user` tại đây.
    """
    
    @staticmethod
    async def get_by_id(db: aiomysql.Connection, user_id: str) -> Optional[dict]:
        """
        Hàm này KHÔNG NÊN được sử dụng để xác thực,
        chỉ dùng trong trường hợp 'order-service' có lý do
        đặc biệt để lưu trữ một bản sao (cache) của user.
        
        Trong 99% trường hợp, hãy lấy data từ token.
        """
        logger.warning(f"Đang gọi hàm get_by_id trong CRUDUser của order-service. "
                       f"Hãy chắc chắn rằng bạn biết mình đang làm gì.")
        # (Nếu bạn có bảng 'users' cache trong CSDL của order-service,
        # logic truy vấn sẽ ở đây. Nếu không, chỉ cần 'pass'.)
        pass