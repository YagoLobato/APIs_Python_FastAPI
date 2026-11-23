from fastapi import APIRouter, Depends, HTTPException
from api.v1.endpoints import cursos, usuarios, artigos

api_router = APIRouter()
api_router.include_router(cursos.router, prefix="/cursos", tags=["cursos"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(artigos.router, prefix="/artigos", tags=["artigos"])