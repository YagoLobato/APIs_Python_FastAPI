from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import autenticar_usuario, criar_token_acesso
from core.deps import get_session, get_usuario_logado
from core.security import gerar_hash_senha
from models.models_usuarios import UsuarioModel
from schemas.usuario_schema import (
    UsuarioSchemaBase,
    UsuarioSchemaCreate,
    UsuarioSchemaArtigos,
    UsuarioSchemaUpdate,
)

router = APIRouter()


def _checar_permissao(usuario_logado: UsuarioModel, usuario_id: int) -> None:
    """Só o próprio usuário ou um admin pode alterar/deletar."""
    if usuario_logado.id != usuario_id and not usuario_logado.eh_admin:
        raise HTTPException(
            detail="Você não tem permissão para realizar esta ação.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


# GET usuário logado
@router.get("/logado", response_model=UsuarioSchemaBase, status_code=status.HTTP_200_OK)
async def get_logado(usuario_logado: UsuarioModel = Depends(get_usuario_logado)):
    return usuario_logado


# POST / Signup
@router.post("/signup", response_model=UsuarioSchemaBase, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    usuario: UsuarioSchemaCreate, session: AsyncSession = Depends(get_session)
):
    novo_usuario = UsuarioModel(
        nome=usuario.nome,
        email=usuario.email,
        senha=gerar_hash_senha(usuario.senha),
        ativo=usuario.ativo,
        eh_admin=False,  # nunca permitir criar admin pelo signup
    )
    session.add(novo_usuario)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            detail="Já existe um usuário com este e-mail.",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    await session.refresh(novo_usuario)
    return novo_usuario


# GET / Listar usuários
@router.get(
    "/",
    response_model=List[UsuarioSchemaBase],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_usuario_logado)],
)
async def listar_usuarios(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(UsuarioModel))
    usuarios: List[UsuarioModel] = result.scalars().all()
    return usuarios


# GET /{usuario_id} (com artigos)
@router.get(
    "/{usuario_id}",
    response_model=UsuarioSchemaArtigos,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_usuario_logado)],
)
async def obter_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    query = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
    result = await session.execute(query)
    usuario = result.scalar_one_or_none()

    if usuario:
        return usuario
    raise HTTPException(
        detail="Usuário não encontrado.", status_code=status.HTTP_404_NOT_FOUND
    )


# PUT /{usuario_id}
@router.put("/{usuario_id}", response_model=UsuarioSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def atualizar_usuario(
    usuario_id: int,
    usuario: UsuarioSchemaUpdate,
    session: AsyncSession = Depends(get_session),
    usuario_logado: UsuarioModel = Depends(get_usuario_logado),
):
    _checar_permissao(usuario_logado, usuario_id)

    query = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
    result = await session.execute(query)
    usuario_up = result.scalar_one_or_none()

    if not usuario_up:
        raise HTTPException(
            detail="Usuário não encontrado.", status_code=status.HTTP_404_NOT_FOUND
        )

    dados = usuario.model_dump(exclude_unset=True, exclude={"id"})

    # Só admin pode mexer no campo eh_admin
    if not usuario_logado.eh_admin:
        dados.pop("eh_admin", None)

    if dados.get("senha"):
        dados["senha"] = gerar_hash_senha(dados["senha"])
    else:
        dados.pop("senha", None)

    for campo, valor in dados.items():
        setattr(usuario_up, campo, valor)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            detail="Já existe um usuário com este e-mail.",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    await session.refresh(usuario_up)
    return usuario_up


# DELETE /{usuario_id}
@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    usuario_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_logado: UsuarioModel = Depends(get_usuario_logado),
):
    _checar_permissao(usuario_logado, usuario_id)

    query = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
    result = await session.execute(query)
    usuario_del = result.scalar_one_or_none()

    if usuario_del:
        await session.delete(usuario_del)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        detail="Usuário não encontrado.", status_code=status.HTTP_404_NOT_FOUND
    )


# POST /login
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    # OAuth2PasswordRequestForm usa "username" para o e-mail
    usuario = await autenticar_usuario(
        email=form_data.username, senha=form_data.password, db=session
    )
    if not usuario:
        raise HTTPException(
            detail="Dados de acesso incorretos.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return {
        "access_token": criar_token_acesso(sub=usuario.email),
        "token_type": "bearer",
    }