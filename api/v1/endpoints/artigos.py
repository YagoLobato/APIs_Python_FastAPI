from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_session, get_usuario_logado
from models.models_usuarios import UsuarioModel
from models.models_artigos import ArtigoModel
from schemas.artigos_schema import ArtigoSchema

router = APIRouter()


async def _buscar_artigo(artigo_id: int, session: AsyncSession) -> ArtigoModel:
    query = select(ArtigoModel).where(ArtigoModel.id == artigo_id)
    result = await session.execute(query)
    artigo = result.scalar_one_or_none()

    if not artigo:
        raise HTTPException(
            detail="Artigo não encontrado.", status_code=status.HTTP_404_NOT_FOUND
        )
    return artigo


def _checar_permissao(usuario_logado: UsuarioModel, artigo: ArtigoModel) -> None:
    """Só o autor do artigo ou um admin pode alterar/deletar."""
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.eh_admin:
        raise HTTPException(
            detail="Você não tem permissão para realizar esta ação.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


# GET / Listar artigos
@router.get(
    "/",
    response_model=List[ArtigoSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_usuario_logado)],
)
async def listar_artigos(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ArtigoModel))
    artigos: List[ArtigoModel] = result.scalars().all()
    return artigos


# POST / Criar artigo
@router.post("/", response_model=ArtigoSchema, status_code=status.HTTP_201_CREATED)
async def criar_artigo(
    artigo: ArtigoSchema,
    session: AsyncSession = Depends(get_session),
    usuario_logado: UsuarioModel = Depends(get_usuario_logado),
):
    novo_artigo = ArtigoModel(
        titulo=artigo.titulo,
        url_fonte=artigo.url_fonte,
        descricao=artigo.descricao,
        usuario_id=usuario_logado.id,  # sempre o usuário logado, ignora o do body
    )
    session.add(novo_artigo)
    await session.commit()
    await session.refresh(novo_artigo)
    return novo_artigo


# GET /{artigo_id}
@router.get(
    "/{artigo_id}",
    response_model=ArtigoSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_usuario_logado)],
)
async def obter_artigo(artigo_id: int, session: AsyncSession = Depends(get_session)):
    return await _buscar_artigo(artigo_id, session)


# PUT /{artigo_id}
@router.put("/{artigo_id}", response_model=ArtigoSchema, status_code=status.HTTP_202_ACCEPTED)
async def atualizar_artigo(
    artigo_id: int,
    artigo: ArtigoSchema,
    session: AsyncSession = Depends(get_session),
    usuario_logado: UsuarioModel = Depends(get_usuario_logado),
):
    artigo_up = await _buscar_artigo(artigo_id, session)
    _checar_permissao(usuario_logado, artigo_up)

    artigo_up.titulo = artigo.titulo
    artigo_up.url_fonte = artigo.url_fonte
    artigo_up.descricao = artigo.descricao
    # usuario_id não é alterado: o autor continua o mesmo

    await session.commit()
    await session.refresh(artigo_up)
    return artigo_up


# DELETE /{artigo_id}
@router.delete("/{artigo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_artigo(
    artigo_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_logado: UsuarioModel = Depends(get_usuario_logado),
):
    artigo_del = await _buscar_artigo(artigo_id, session)
    _checar_permissao(usuario_logado, artigo_del)

    await session.delete(artigo_del)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)