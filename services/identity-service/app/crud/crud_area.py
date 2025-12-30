from typing import Optional
import aiomysql
import logging

logger = logging.getLogger(__name__)

# app/crud/crud_area.py

class CRUDArea:
    
    @staticmethod
    async def find_area_by_coordinates(
        db: aiomysql.Connection, 
        latitude: float,   # Tham số mới
        longitude: float   # Tham số mới
    ) -> Optional[str]:
        """
        Tìm area_id dựa trên latitude và longitude riêng biệt.
        """
        
        # CÔNG THỨC: ST_Distance_Sphere(Point1, Point2)
        # Point1: Tâm vùng (lấy từ cột center_longitude, center_latitude)
        # Point2: Vị trí SME (được tạo từ tham số truyền vào)
        # LƯU Ý QUAN TRỌNG: Hàm POINT nhận tham số theo thứ tự (Longitude, Latitude)
        
        query = """
            SELECT area_id
            FROM areas
            WHERE
                status = 'ACTIVE' AND
                ST_Distance_Sphere(
                    POINT(center_longitude, center_latitude), 
                    POINT(%s, %s) 
                ) <= (radius_km * 1000)
            LIMIT 1; 
        """
        
        try:
            async with db.cursor() as cursor:
                # Truyền tham số theo thứ tự: (longitude, latitude) để khớp với POINT(%s, %s)
                await cursor.execute(query, (longitude, latitude))
                result = await cursor.fetchone()
                
                if result:
                    logger.info(f"✅ Tọa độ ({latitude}, {longitude}) thuộc Area ID: {result[0]}")
                    return result[0]
                
                logger.info(f"⚠️ Không tìm thấy Area nào chứa tọa độ ({latitude}, {longitude})")
                return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi tìm area_id: {e}")
            return None