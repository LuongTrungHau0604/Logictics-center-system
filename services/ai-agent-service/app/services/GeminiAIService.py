import google.generativeai as genai
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.LogisticsAgentService import process_logistics_route

logger = logging.getLogger(__name__)

class RouteCalculationRequest(BaseModel):
    """Schema cho route calculation request"""
    business_address: str
    receiver_address: str
    required_capacity: int = 1

class RouteCalculationResponse(BaseModel):
    """Schema cho route calculation response"""
    status: str
    message: str
    business_coords: Optional[Dict[str, float]] = None
    receiver_coords: Optional[Dict[str, float]] = None
    warehouse: Optional[Dict[str, Any]] = None
    pickup_distance_km: Optional[float] = None
    delivery_distance_km: Optional[float] = None
    total_distance_km: Optional[float] = None
    route_summary: Optional[Dict[str, str]] = None
    geocoding_type: Optional[str] = None
    error_type: Optional[str] = None

class GeminiAIService:
    """
    Gemini AI Service với Function Calling (Tools) cho Logistics
    """
    
    def __init__(self):
        """Khởi tạo Gemini AI service"""
        try:
            # Configure Gemini API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Định nghĩa tools cho Gemini
            self.tools = self._define_tools()
            
            # Khởi tạo model với tools
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",  # Hoặc gemini-1.5-flash cho tốc độ
                tools=self.tools,
                system_instruction=self._get_system_instruction()
            )
            
            logger.info("✅ Gemini AI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            raise
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """
        Định nghĩa tools (functions) cho Gemini AI (ĐÃ SỬA LỖI - Xóa "default")
        """
        return [
            {
                "function_declarations": [
                    {
                        "name": "calculate_logistics_route",
                        "description": """
                        Tính toán tuyến đường logistics tối ưu từ địa chỉ doanh nghiệp đến địa chỉ người nhận.
                        Function này sẽ:
                        1. Geocoding địa chỉ thành tọa độ GPS chính xác
                        2. Tìm kho hàng gần nhất có đủ dung lượng
                        3. Tính toán khoảng cách đường bộ thực tế
                        4. Đưa ra route tối ưu cho shipper
                        
                        Sử dụng khi user hỏi về:
                        - Tính phí vận chuyển
                        - Tìm đường đi tối ưu
                        - Ước tính thời gian giao hàng
                        - Kiểm tra khả năng giao hàng đến một địa chỉ
                        - So sánh chi phí vận chuyển
                        """,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "business_address": {
                                    "type": "string",
                                    "description": "Địa chỉ đầy đủ của doanh nghiệp/điểm gửi hàng. Ví dụ: '1 Đ. Phú Thuận, Phú Thuận, Quận 7, Thành phố Hồ Chí Minh, Việt Nam'"
                                },
                                "receiver_address": {
                                    "type": "string", 
                                    "description": "Địa chỉ đầy đủ của người nhận hàng. Ví dụ: '18 Đ. Phạm Nhữ Tăng, Phường 4, Quận 8, Thành phố Hồ Chí Minh 73053, Việt Nam'"
                                },
                                "required_capacity": {
                                    "type": "integer",
                                    "description": "Dung lượng yêu cầu (số lượng đơn hàng). Mặc định là 1"
                                    # Dòng "default": 1  <-- ĐÃ BỊ XÓA
                                }
                            },
                            "required": ["business_address", "receiver_address"]
                        }
                    },
                    {
                        "name": "get_shipping_cost_estimate",
                        "description": """
                        Ước tính chi phí vận chuyển dựa trên khoảng cách và thông tin route.
                        Function này tính toán:
                        1. Chi phí cố định
                        2. Chi phí theo khoảng cách
                        3. Phụ phí (nếu có)
                        4. Tổng chi phí ước tính
                        """,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "total_distance_km": {
                                    "type": "number",
                                    "description": "Tổng khoảng cách vận chuyển (km)"
                                },
                                "weight_kg": {
                                    "type": "number", 
                                    "description": "Khối lượng hàng hóa (kg)"
                                    # Dòng "default": 1.0  <-- ĐÃ BỊ XÓA
                                },
                                "delivery_type": {
                                    "type": "string",
                                    "enum": ["standard", "express", "same_day"],
                                    "description": "Loại giao hàng: standard (thường), express (nhanh), same_day (trong ngày)"
                                    # Dòng "default": "standard"  <-- ĐÃ BỊ XÓA
                                },
                                "is_fragile": {
                                    "type": "boolean",
                                    "description": "Hàng dễ vỡ (cần đóng gói đặc biệt)"
                                    # Dòng "default": false  <-- ĐÃ BỊ XÓA
                                }
                            },
                            "required": ["total_distance_km"]
                        }
                    }
                    # (Bạn có thể thêm các tool khác như 'predict_delivery_demand' ở đây nếu muốn)
                ]
            }
        ]
    
    def _get_system_instruction(self) -> str:
        """
        System instruction cho Gemini AI (Đã cập nhật)
        """
        return """
        Bạn là AI Assistant chuyên về logistics và vận chuyển tại Việt Nam.

        NHIỆM VỤ:
        - Hỗ trợ tính toán tuyến đường vận chuyển tối ưu
        - Ước tính chi phí và thời gian giao hàng
        - Trả lời các câu hỏi về vận chuyển, giao nhận

        NGUYÊN TẮC QUAN TRỌNG:
        1. XEM XÉT LỊCH SỬ CHAT: Luôn luôn kiểm tra 'chat_history' trước.
        2. KHÔNG CHẠY LẠI TOOL: Nếu thông tin bạn cần (như 'total_distance_km') ĐÃ CÓ trong 'chat_history' (từ 'function_result' của Lần 1), HÃY SỬ DỤNG LẠI nó. ĐỪNG gọi lại 'calculate_logistics_route' (Tool 1) nếu không cần thiết.
        3. CHỈ GỌI TOOL KHI CẦN: Chỉ gọi tool khi người dùng cung cấp thông tin MỚI hoặc yêu cầu MỚI.
        4. HỎI NẾU THIẾU: Nếu bạn cần gọi 'get_shipping_cost_estimate' (Tool 2) nhưng thiếu 'weight_kg' hoặc 'delivery_type', HÃY HỎI LẠI người dùng.
        
        ĐỊNH DẠNG ĐỊA CHỈ VIỆT NAM:
        - Luôn yêu cầu địa chỉ đầy đủ: Số nhà + Đường + Phường/Xã + Quận/Huyện + Thành phố/Tỉnh
        """
    
    async def calculate_logistics_route_tool(
        self, 
        db: Session,
        business_address: str, 
        receiver_address: str, 
        required_capacity: int = 1
    ) -> Dict[str, Any]:
        """
        Tool implementation cho route calculation
        """
        try:
            logger.info(f"🤖 AI Tool: Calculating route")
            logger.info(f"   📍 From: {business_address}")
            logger.info(f"   📍 To: {receiver_address}")
            logger.info(f"   📦 Capacity: {required_capacity}")
            
            # Gọi logistics service
            result = await process_logistics_route(
                db=db,
                business_address=business_address,
                receiver_address=receiver_address,
                required_capacity=required_capacity
            )
            
            logger.info(f"✅ AI Tool result: {result.get('status', 'UNKNOWN')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in AI tool: {e}")
            return {
                "status": "ERROR",
                "message": f"Tool execution error: {str(e)}",
                "error_type": "TOOL_ERROR"
            }
    
    def get_shipping_cost_estimate_tool(
        self,
        total_distance_km: float,
        weight_kg: float = 1.0,
        delivery_type: str = "standard",
        is_fragile: bool = False
    ) -> Dict[str, Any]:
        """
        Tool implementation cho shipping cost estimation
        """
        try:
            logger.info(f"🤖 AI Tool: Calculating shipping cost")
            
            # Bảng giá cơ bản (VND)
            base_prices = {
                "standard": 15000,    # 15k VND cố định
                "express": 25000,     # 25k VND cố định
                "same_day": 40000     # 40k VND cố định
            }
            
            # Chi phí theo km
            distance_prices = {
                "standard": 3000,     # 3k VND/km
                "express": 4000,      # 4k VND/km  
                "same_day": 6000      # 6k VND/km
            }
            
            # Tính chi phí cơ bản
            base_cost = base_prices.get(delivery_type, base_prices["standard"])
            distance_cost = total_distance_km * distance_prices.get(delivery_type, distance_prices["standard"])
            
            # Phụ phí theo trọng lượng (> 5kg)
            weight_surcharge = max(0, (weight_kg - 5) * 2000) if weight_kg > 5 else 0
            
            # Phụ phí hàng dễ vỡ
            fragile_surcharge = base_cost * 0.2 if is_fragile else 0
            
            # Tổng chi phí
            total_cost = base_cost + distance_cost + weight_surcharge + fragile_surcharge
            
            # Ước tính thời gian
            delivery_times = {
                "standard": "2-3 ngày",
                "express": "1-2 ngày", 
                "same_day": "4-8 giờ"
            }
            
            result = {
                "status": "SUCCESS",
                "cost_breakdown": {
                    "base_cost": base_cost,
                    "distance_cost": distance_cost,
                    "weight_surcharge": weight_surcharge,
                    "fragile_surcharge": fragile_surcharge,
                    "total_cost": round(total_cost, 0)
                },
                "delivery_info": {
                    "type": delivery_type,
                    "estimated_time": delivery_times.get(delivery_type, "2-3 ngày"),
                    "distance_km": total_distance_km,
                    "weight_kg": weight_kg
                },
                "formatted_cost": f"{int(total_cost):,} VND"
            }
            
            logger.info(f"✅ Cost calculated: {int(total_cost):,} VND")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating cost: {e}")
            return {
                "status": "ERROR",
                "message": f"Cost calculation error: {str(e)}"
            }
    
    # Trong file: app/services/GeminiAIService.py

    async def chat_with_tools(self, db: Session, user_message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Chat với Gemini AI sử dụng function calling (Đã sửa lỗi, hỗ trợ vòng lặp)
        """
        try:
            logger.info(f"🤖 User message: {user_message}")
            
            # Tạo chat session
            chat_session = self.model.start_chat(history=chat_history or [])
            
            # Gửi message đầu tiên
            response = chat_session.send_message(user_message)
            
            # Khởi tạo các biến để lưu tool cuối cùng
            last_tool_result = None
            last_tool_name = None
            
            # BẮT ĐẦU VÒNG LẶP:
            # Tiếp tục lặp tantrai_response nào AI còn yêu cầu gọi hàm
            while True:
                if not response.candidates[0].content.parts or not hasattr(response.candidates[0].content.parts[0], 'function_call'):
                    # THOÁT LẶP: AI đã trả về text cuối cùng
                    logger.info("✅ AI finished reasoning, returning text response.")
                    break 
                
                # AI yêu cầu gọi 1 hàm
                function_call = response.candidates[0].content.parts[0].function_call
                
                # --- SỬA LỖI: THÊM BƯỚC KIỂM TRA TÊN HÀM ---
                if not function_call.name:
                    logger.error(f"❌ AI trả về một FunctionCall nhưng không có 'name'. Bỏ qua.")
                    # Gửi một thông báo lỗi chung và thoát
                    response = chat_session.send_message(
                        "Internal error: AI returned a function call with an empty name."
                    )
                    break # Thoát vòng lặp
                # -----------------------------------------------
                
                function_name = function_call.name
                function_args = dict(function_call.args or {})
                
                # Lưu lại tool cuối cùng
                last_tool_name = function_name
                
                logger.info(f"🔧 AI wants to call function: {function_name}")
                logger.info(f"📝 Arguments: {function_args}")
                
                tool_result = None
                
                # Thực thi hàm
                try:
                    if function_name == "calculate_logistics_route":
                        tool_result = await self.calculate_logistics_route_tool(
                            db=db,
                            **function_args
                        )
                    elif function_name == "get_shipping_cost_estimate":
                        tool_result = self.get_shipping_cost_estimate_tool(**function_args)
                    else:
                        tool_result = {"status": "ERROR", "message": f"Unknown function: {function_name}"}
                
                except Exception as e:
                    logger.error(f"❌ Lỗi khi đang chạy tool '{function_name}': {e}", exc_info=True)
                    tool_result = {"status": "ERROR", "message": f"Tool execution failed: {str(e)}"}
                
                # Lưu lại kết quả tool cuối cùng
                last_tool_result = tool_result
                
                # Gửi kết quả của tool ngược lại cho AI
                function_response = genai.protos.Content(
                    parts=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_name,
                            response={"result": tool_result}
                        )
                    )]
                )
                
                # Gửi kết quả tool và chờ phản hồi MỚI của AI
                response = chat_session.send_message(function_response)
                # Vòng lặp tiếp tục, AI sẽ nhận kết quả và quyết định
                # (gọi tool mới, hoặc trả về text)
            
            # KẾT THÚC VÒNG LẶP (response bây giờ là text)
            
            return {
                "status": "SUCCESS", 
                "ai_response": response.text,
                "function_called": last_tool_name, # Trả về tool cuối cùng
                "function_result": last_tool_result,
                "chat_history": chat_session.history
            }
            
        except Exception as e:
            # Lỗi này bắt các lỗi ngoài vòng lặp (ví dụ: lỗi send_message ban đầu)
            logger.error(f"❌ Error in AI chat: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "message": f"AI chat error: {str(e)}",
                "ai_response": "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu. Vui lòng thử lại sau."
            }
            

# Singleton instance
gemini_service: Optional[GeminiAIService] = None

def get_gemini_service() -> GeminiAIService:
    """
    Get singleton Gemini service instance
    """
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiAIService()
    return gemini_service

# Utility function
async def process_ai_query(db: Session, user_message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Process user query với Gemini AI
    """
    service = get_gemini_service()
    return await service.chat_with_tools(db, user_message, chat_history)