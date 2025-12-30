from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any
from app import models
import logging

logger = logging.getLogger(__name__)

class CRUDDispatch:
    def get_dispatch_summary(self, db: Session) -> List[Dict[str, Any]]:
        try:
            db.commit()
            # 1. Query lấy tất cả các Leg
            # Sử dụng outerjoin để tránh mất dữ liệu nếu quan hệ bị thiếu
            query = (
                select(models.OrderJourneyLeg, models.Order, models.SME)
                .join(models.Order, models.OrderJourneyLeg.order_id == models.Order.order_id)
                .outerjoin(models.SME, models.Order.sme_id == models.SME.sme_id)
                .order_by(models.OrderJourneyLeg.order_id, models.OrderJourneyLeg.sequence)
            )
            
            results = db.execute(query).all()
            
            orders_map = {}
            
            for leg, order, sme in results:
                order_id = leg.order_id
                
                if order_id not in orders_map:
                    # Khởi tạo object an toàn với giá trị mặc định
                    orders_map[order_id] = {
                        "id": str(order_id), # Ép kiểu str cho chắc chắn
                        "code": order.order_code or "N/A",
                        "from_location": "Unknown",
                        "to_location": "Unknown",
                        "status": order.status or "PENDING",
                        "priority": "medium", 
                        "total_distance": 0.0,
                        "total_legs": 0,
                        "created_at": str(order.created_at) if order.created_at else ""
                    }
                
                current = orders_map[order_id]
                current["total_legs"] += 1
                
                # Cộng dồn khoảng cách (xử lý None)
                dist = float(leg.estimated_distance) if leg.estimated_distance else 0.0
                current["total_distance"] += dist
                
                # Logic điểm đi (Sequence 1)
                if leg.sequence == 1:
                    if leg.origin_sme_id and sme:
                        current["from_location"] = sme.address or sme.business_name or "SME Location"
                    elif leg.origin_warehouse_id:
                        current["from_location"] = f"Warehouse {leg.origin_warehouse_id}"
                    elif order.receiver_address and leg.leg_type == models.LegType.PICKUP:
                         # Fallback nếu không có thông tin warehouse/sme
                         current["from_location"] = "Pickup Point"

                # Logic điểm đến (Delivery)
                if leg.leg_type == models.LegType.DELIVERY:
                    if leg.destination_is_receiver:
                        current["to_location"] = order.receiver_address or "Customer Address"
                    elif leg.destination_warehouse_id:
                        current["to_location"] = f"Warehouse {leg.destination_warehouse_id}"

            # Trả về list
            return list(orders_map.values())
            
        except Exception as e:
            logger.error(f"❌ Error in get_dispatch_summary: {str(e)}")
            # Ném lỗi ra để API endpoint bắt được
            raise e

dispatch = CRUDDispatch()