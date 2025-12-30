from fastapi import APIRouter

from app.api.v1.endpoints import (
    optimization,
    ai_insights,
    order_processing,
    geocoding,
    warehouse,
    ai_insights,
    ai_chat, 
    ai_batch_optimizer, 
    area, 
    dispatch
)

api_router = APIRouter()

api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["ai-insights"])
api_router.include_router(order_processing.router, prefix="/order-processing", tags=["order-processing"])
api_router.include_router(geocoding.router, prefix="/geocoding", tags=["geocoding"])
api_router.include_router(warehouse.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(ai_chat.router, prefix="/ai-insights", tags=["ai-insights"])
api_router.include_router(ai_batch_optimizer.router, prefix="/ai-batch-optimizer", tags=["ai-batch-optimizer"])
api_router.include_router(area.router, prefix="/areas", tags=["Areas"])
api_router.include_router(dispatch.router, prefix="/dispatch", tags=["Dispatch"])
# <<< THÊM DÒNG NÀY
