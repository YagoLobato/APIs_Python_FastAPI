from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.deps import get_session
from models.models_curso import CursoModel
from schemas.curso_schema import CursoSchema

router = APIRouter()


@router.get("/", response_model=List[CursoSchema], status_code=status.HTTP_200_OK)
async def listar_cursos(session: AsyncSession = Depends(get_session)):
    async with session as db:
        query = select(CursoModel)
        result = await db.execute(query)
        cursos: List[CursoModel] = result.scalars().all()
        return cursos


@router.post("/", response_model=CursoSchema, status_code=status.HTTP_201_CREATED)
async def criar_curso(curso: CursoSchema, session: AsyncSession = Depends(get_session)):
    novo_curso = CursoModel(titulo=curso.titulo, aulas=curso.aulas, horas=curso.horas)
    session.add(novo_curso)
    await session.commit()
    await session.refresh(novo_curso)
    return novo_curso


@router.get("/{curso_id}", response_model=CursoSchema, status_code=status.HTTP_200_OK)
async def obter_curso(curso_id: int, session: AsyncSession = Depends(get_session)):
    async with session as db:
        query = select(CursoModel).filter(CursoModel.id == curso_id)
        result = await db.execute(query)
        curso = result.scalar_one_or_none()

        if curso:
            return curso
        raise HTTPException(
            detail="Curso não encontrado.",
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.put("/{curso_id}", response_model=CursoSchema, status_code=status.HTTP_202_ACCEPTED)
async def atualizar_curso(curso_id: int, curso: CursoSchema, session: AsyncSession = Depends(get_session)):
    async with session as db:
        query = select(CursoModel).filter(CursoModel.id == curso_id)
        result = await db.execute(query)
        curso_up = result.scalar_one_or_none()

        if curso_up:
            curso_up.titulo = curso.titulo
            curso_up.aulas = curso.aulas
            curso_up.horas = curso.horas

            await db.commit()
            await db.refresh(curso_up)
            return curso_up
        raise HTTPException(
            detail="Curso não encontrado.",
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_curso(curso_id: int, session: AsyncSession = Depends(get_session)):
    async with session as db:
        query = select(CursoModel).filter(CursoModel.id == curso_id)
        result = await db.execute(query)
        curso_del = result.scalar_one_or_none()

        if curso_del:
            await db.delete(curso_del)
            await db.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Curso não encontrado.",
            status_code=status.HTTP_404_NOT_FOUND
        )