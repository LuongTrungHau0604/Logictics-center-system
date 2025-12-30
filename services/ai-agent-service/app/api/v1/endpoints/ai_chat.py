from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
from app.db.session import get_db
from app.services.GeminiAIService import process_ai_query

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    """Schema cho chat message"""
    role: str  # "user" hoặc "assistant"
    content: str

class ChatRequest(BaseModel):
    """Schema cho chat request"""
    message: str
    chat_history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    """Schema cho chat response"""
    status: str
    ai_response: str
    function_called: Optional[str] = None
    function_result: Optional[Dict[str, Any]] = None

@router.post("/ai/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat với AI Assistant cho logistics
    """
    try:
        # Convert Pydantic models to dict for Gemini
        history = []
        if request.chat_history:
            for msg in request.chat_history:
                history.append({
                    "role": msg.role,
                    "parts": [msg.content]
                })
        
        # Process với AI
        result = await process_ai_query(
            db=db,
            user_message=request.message,
            chat_history=history
        )
        
        if result["status"] == "ERROR":
            raise HTTPException(status_code=500, detail=result.get("message", "AI processing error"))
        
        return ChatResponse(
            status=result["status"],
            ai_response=result["ai_response"],
            function_called=result.get("function_called"),
            function_result=result.get("function_result")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@router.get("/ai/tools")
async def get_available_tools():
    """
    Lấy danh sách tools có sẵn
    """
    from app.services.GeminiAIService import get_gemini_service
    
    service = get_gemini_service()
    return {
        "tools": service.tools,
        "capabilities": [
            "Tính toán tuyến đường logistics tối ưu",
            "Ước tính chi phí vận chuyển", 
            "Tư vấn giải pháp giao nhận",
            "Phân tích hiệu quả logistics"
        ]
    }