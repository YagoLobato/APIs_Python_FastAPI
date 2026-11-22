from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_session
from models.models_curso import CursoModel
from schema.schemas_curso import CursoSchema

router = APIRouter()

@router.get("/cursos", status_code=status.HTTP_200_OK)
async def listar_cursos(session: AsyncSession = Depends(get_session)):
    async with session.begin():
        query = "SELECT * FROM cursos"
        result = await session.execute(query)
        cursos = result.scalars().all()
    return cursos

@router.post("/cursos", status_code=status.HTTP_201_CREATED)
async def criar_curso(curso: CursoSchema, session: AsyncSession = Depends(get_session)):
    curso_model = CursoModel(titulo=curso.titulo, aulas=curso.aulas, horas=curso.horas)
    session.add(curso_model)
    await session.commit()
    await session.refresh(curso_model)
    return curso_model

@router.get("/cursos/{curso_id}", status_code=status.HTTP_200_OK)
async def obter_curso(curso_id: int, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        query = "SELECT * FROM cursos WHERE id = :curso_id"
        result = await session.execute(query, {"curso_id": curso_id})
        curso = result.scalar_one_or_none()
    if curso is None:
        return {"message": "Curso não encontrado"}
    return curso

@router.put("/cursos/{curso_id}", status_code=status.HTTP_200_OK)
async def atualizar_curso(curso_id: int, curso: CursoSchema, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        query = "SELECT * FROM cursos WHERE id = :curso_id"
        result = await session.execute(query, {"curso_id": curso_id})
        curso_model = result.scalar_one_or_none()
        if curso_model is None:
            return {"message": "Curso não encontrado"}
        curso_model.titulo = curso.titulo
        curso_model.aulas = curso.aulas
        curso_model.horas = curso.horas
        await session.commit()
        await session.refresh(curso_model)
    return curso_model

@router.delete("/cursos/{curso_id}", status_code=status.HTTP_200_OK)
async def deletar_curso(curso_id: int, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        query = "SELECT * FROM cursos WHERE id = :curso_id"
        result = await session.execute(query, {"curso_id": curso_id})
        curso_model = result.scalar_one_or_none()
        if curso_model is None:
            return {"message": "Curso não encontrado"}
        await session.delete(curso_model)
        await session.commit()
    return {"message": "Curso deletado com sucesso"}