from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declared_attr

class Base(DeclarativeBase):
    """
    Lớp Base cơ sở cho tất cả các model SQLAlchemy.

    Tất cả các model (bảng) trong CSDL của bạn sẽ kế thừa từ lớp này.
    Ví dụ: class Order(Base): ...
    
    SQLAlchemy sẽ sử dụng lớp Base này để thu thập "siêu dữ liệu" (metadata)
    về tất cả các bảng bạn định nghĩa.
    """
    
    # __abstract__ = True báo cho SQLAlchemy biết rằng 
    # lớp Base này không phải là một bảng cần được tạo trong CSDL.
    __abstract__ = True

    # --- TÙY CHỌN (RECOMMENDED) ---
    # Bạn có thể thêm một trình tạo tên bảng tự động ở đây
    # để bạn không phải gõ __tablename__ cho mỗi model.
    # Ví dụ: class User -> tên bảng là "user"
    #        class OrderJourneyLeg -> tên bảng là "orderjourneyleg"
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Tự động tạo tên bảng từ tên class (viết thường).
        """
        return cls.__name__.lower()