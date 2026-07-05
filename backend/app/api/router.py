from fastapi import APIRouter

from app.api.endpoints import analysis, arrangements, chat, export, songs

api_router = APIRouter()
api_router.include_router(songs.router, prefix="/songs", tags=["songs"])
api_router.include_router(analysis.router, prefix="/songs", tags=["analysis"])
api_router.include_router(arrangements.router, prefix="/songs", tags=["arrangements"])
api_router.include_router(chat.router, prefix="/songs", tags=["chat"])
api_router.include_router(export.router, prefix="/songs", tags=["export"])
