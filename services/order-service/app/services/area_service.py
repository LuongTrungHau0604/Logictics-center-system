import aiomysql
import logging
import math
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


logger.setLevel(logging.INFO)  # ← THÊM DÒNG NÀY

# ✅ Thêm console handler nếu chưa có
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    
class AreaService:
    """
    Service để xác định area_id dựa trên tọa độ đơn hàng.
    """
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Tính khoảng cách Haversine giữa 2 điểm (km).
        """
        # (Logic này đã ổn, không thay đổi)
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        r = 6371.0
        return r * c
    
    @staticmethod
    async def find_area_by_coordinates(
        db: aiomysql.Connection, 
        latitude: float, 
        longitude: float
    ) -> Optional[str]:
        """
        Tìm area_id phù hợp nhất dựa trên tọa độ.
        """
        print(f"🔧 DIRECT PRINT: Starting find_area_by_coordinates with ({latitude}, {longitude})")
        logger.warning(f"🗺️ FORCED WARNING: Đang tìm Area cho tọa độ: ({latitude:.6f}, {longitude:.6f})")
        
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                # ✅ FIX: Hoán đổi lại ST_X và ST_Y cho đúng
                query = """
                    SELECT 
                        area_id, name, type, radius_km,
                        ST_Y(center_coordinates) as center_longitude,  -- ✅ ST_Y = longitude  
                        ST_X(center_coordinates) as center_latitude    -- ✅ ST_X = latitude
                    FROM areas 
                    WHERE status = 'ACTIVE' 
                    AND center_coordinates IS NOT NULL
                    ORDER BY 
                        CASE type 
                            WHEN 'DISTRICT' THEN 1
                            WHEN 'CITY' THEN 2  
                            WHEN 'REGION' THEN 3
                            WHEN 'CUSTOM' THEN 4
                        END
                """
                
                logger.warning(f"🔧 EXECUTING SQL QUERY...")
                await cursor.execute(query)
                areas = await cursor.fetchall()
                
                print(f"🔧 DIRECT PRINT: Found {len(areas)} areas")
                logger.warning(f"🔍 FOUND {len(areas)} AREAS")
                
                if not areas:
                    logger.warning("⚠️ Không tìm thấy Area nào (ACTIVE, có tọa độ) trong CSDL.")
                    return None
                
                # Debug areas
                for i, area in enumerate(areas):
                    print(f"  Area {i+1}: {area['area_id']} - {area['name']} (Type: {area['type']})")
                    logger.warning(f"  Area {i+1}: {area['area_id']} - {area['name']} (Type: {area['type']})")
                
                best_area = None
                min_distance = float('inf')
                
                for area in areas:
                    try:
                        # ✅ Giờ đây sẽ đúng:
                        center_lat = float(area['center_latitude'])    # ST_X = 10.77 ✅
                        center_lon = float(area['center_longitude'])   # ST_Y = 106.7 ✅
                        radius_km = float(area['radius_km'])
                        
                        print(f"    Processing area {area['area_id']}: center=({center_lat}, {center_lon}), radius={radius_km}")
                        logger.warning(f"    Processing area {area['area_id']}: center=({center_lat:.6f}, {center_lon:.6f}), radius={radius_km}")
                        
                    except (TypeError, ValueError) as e:
                        logger.warning(f"⚠️ Bỏ qua Area {area.get('area_id')} do dữ liệu không hợp lệ: {e}")
                        continue

                    distance = AreaService.calculate_distance(
                        latitude, longitude,
                        center_lat, center_lon
                    )
                    
                    print(f"    Distance to {area['area_id']}: {distance:.2f}km (max: {radius_km}km)")
                    logger.warning(f"  -> Distance to {area['area_id']}: {distance:.2f}km (max: {radius_km}km)")
                    
                    if distance <= radius_km:
                        print(f"    ✅ MATCH! {area['area_id']} is within range")
                        logger.warning(f"  ✅ MATCH! {area['area_id']} is within range")
                        
                        if distance < min_distance:
                            best_area = area
                            min_distance = distance
                            
                            if area['type'] == 'DISTRICT':
                                print(f"    🎯 District found, stopping search")
                                logger.warning(f"🎯 District found, stopping search")
                                break
                
                if best_area:
                    result = best_area['area_id']
                    print(f"🎯 FINAL RESULT: {result}")
                    logger.warning(f"🎯 FINAL RESULT: {result}")
                    return result
                else:
                    print(f"⚠️ No area covers coordinates ({latitude}, {longitude})")
                    logger.warning(f"⚠️ No area covers coordinates ({latitude}, {longitude})")
                    return None
                    
        except Exception as e:
            print(f"❌ EXCEPTION in find_area_by_coordinates: {e}")
            logger.error(f"❌ EXCEPTION in find_area_by_coordinates: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            raise e

    # ✅ Cũng fix get_area_info method
    @staticmethod
    async def get_area_info(db: aiomysql.Connection, area_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết của một area.
        """
        logger.info(f"📦 Đang lấy thông tin cho Area ID: {area_id}")
        
        async with db.cursor(aiomysql.DictCursor) as cursor:
            query = """
                SELECT 
                    area_id, name, description, type, status,
                    radius_km,
                    ST_Y(center_coordinates) as center_longitude,  -- ✅ ST_Y = longitude
                    ST_X(center_coordinates) as center_latitude    -- ✅ ST_X = latitude
                FROM areas 
                WHERE area_id = %s
            """
            logger.debug(f"Đang thực thi query lấy Area {area_id}...")
            await cursor.execute(query, (area_id,))
            result = await cursor.fetchone()
            
            if result:
                logger.info(f"✅ Tìm thấy thông tin cho Area: {area_id}")
                return dict(result)
            else:
                logger.warning(f"⚠️ Không tìm thấy Area nào trong CSDL có ID: {area_id}")
                return None
                
    

# Export singleton
area_service = AreaService()