# api/v1/router.py
from fastapi import APIRouter
from api.v1.endpoints import users,auth,sme, employee

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sme.router, prefix="/sme", tags=["sme"])
api_router.include_router(employee.router, prefix="/employee", tags=["employee"])