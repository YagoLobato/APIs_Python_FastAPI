"""Testes dos endpoints de artigos.

Requisitos:
  - fixture `client` (httpx.AsyncClient apontando para o app, com banco de testes) no conftest.py
  - pytest e pytest-asyncio

Cada teste cria os próprios dados (usuários com e-mails únicos e seus artigos),
então não depende da ordem de execução nem de dados já existentes no banco.
"""
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import update

from core.config import settings
from core.database import async_session
from models.models_usuarios import UsuarioModel

pytestmark = pytest.mark.asyncio

BASE_URL = f"{settings.API_V1_STR}/artigos"
USUARIOS_URL = f"{settings.API_V1_STR}/usuarios"
SENHA_PADRAO = "Senha@12345"
ID_INEXISTENTE = 999_999_999


# --------------------------------------------------------------------------- #
# Helpers e fixtures
# --------------------------------------------------------------------------- #
def _email_unico() -> str:
    return f"user_{uuid.uuid4().hex[:12]}@example.com"


async def _criar_usuario(client: AsyncClient, **extra) -> dict:
    dados = {
        "nome": "Usuário Teste",
        "email": _email_unico(),
        "senha": SENHA_PADRAO,
        **extra,
    }
    response = await client.post(f"{USUARIOS_URL}/signup", json=dados)
    assert response.status_code == 201, response.text
    return {**dados, "id": response.json()["id"]}


async def _login(client: AsyncClient, email: str, senha: str = SENHA_PADRAO) -> dict:
    response = await client.post(
        f"{USUARIOS_URL}/login", data={"username": email, "password": senha}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _promover_admin(usuario_id: int) -> None:
    # O signup nunca cria admin, então promovemos direto no banco de testes.
    async with async_session() as session:
        await session.execute(
            update(UsuarioModel)
            .where(UsuarioModel.id == usuario_id)
            .values(eh_admin=True)
        )
        await session.commit()


def _payload_artigo(usuario_id: int, **extra) -> dict:
    return {
        "titulo": f"Artigo {uuid.uuid4().hex[:8]}",
        "url_fonte": "https://example.com/artigo",
        "descricao": "Descrição do artigo de teste",
        "usuario_id": usuario_id,
        **extra,
    }


@pytest_asyncio.fixture
async def usuario(client: AsyncClient) -> dict:
    dados = await _criar_usuario(client)
    dados["headers"] = await _login(client, dados["email"])
    return dados


@pytest_asyncio.fixture
async def outro_usuario(client: AsyncClient) -> dict:
    dados = await _criar_usuario(client, nome="Outro Usuário")
    dados["headers"] = await _login(client, dados["email"])
    return dados


@pytest_asyncio.fixture
async def admin(client: AsyncClient) -> dict:
    dados = await _criar_usuario(client, nome="Admin")
    await _promover_admin(dados["id"])
    dados["headers"] = await _login(client, dados["email"])
    return dados


@pytest_asyncio.fixture
async def artigo(client: AsyncClient, usuario: dict) -> dict:
    """Artigo já criado, pertencente a `usuario`."""
    response = await client.post(
        f"{BASE_URL}/",
        json=_payload_artigo(usuario["id"]),
        headers=usuario["headers"],
    )
    assert response.status_code == 201, response.text
    return response.json()


# --------------------------------------------------------------------------- #
# Proteção das rotas
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "metodo, caminho",
    [
        ("GET", "/"),
        ("POST", "/"),
        ("GET", "/1"),
        ("PUT", "/1"),
        ("DELETE", "/1"),
    ],
)
async def test_rotas_protegidas_exigem_token(client: AsyncClient, metodo, caminho):
    response = await client.request(
        metodo, f"{BASE_URL}{caminho}", json=_payload_artigo(1)
    )
    assert response.status_code == 401


# --------------------------------------------------------------------------- #
# Criar
# --------------------------------------------------------------------------- #
async def test_criar_artigo(client: AsyncClient, usuario: dict):
    payload = _payload_artigo(usuario["id"])
    response = await client.post(
        f"{BASE_URL}/", json=payload, headers=usuario["headers"]
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == payload["titulo"]
    assert data["url_fonte"] == payload["url_fonte"]
    assert data["descricao"] == payload["descricao"]
    assert data["usuario_id"] == usuario["id"]
    assert "id" in data


async def test_criar_artigo_ignora_usuario_id_do_body(
    client: AsyncClient, usuario: dict, outro_usuario: dict
):
    payload = _payload_artigo(outro_usuario["id"])
    response = await client.post(
        f"{BASE_URL}/", json=payload, headers=usuario["headers"]
    )
    assert response.status_code == 201
    assert response.json()["usuario_id"] == usuario["id"]


async def test_criar_artigo_payload_invalido(client: AsyncClient, usuario: dict):
    payload = _payload_artigo(usuario["id"])
    del payload["titulo"]
    response = await client.post(
        f"{BASE_URL}/", json=payload, headers=usuario["headers"]
    )
    assert response.status_code == 422


# --------------------------------------------------------------------------- #
# Listar / obter
# --------------------------------------------------------------------------- #
async def test_listar_artigos(client: AsyncClient, usuario: dict, artigo: dict):
    response = await client.get(f"{BASE_URL}/", headers=usuario["headers"])
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert artigo["id"] in [a["id"] for a in data]


async def test_listar_artigos_de_outros_usuarios(
    client: AsyncClient, outro_usuario: dict, artigo: dict
):
    # qualquer usuário logado enxerga os artigos dos demais
    response = await client.get(f"{BASE_URL}/", headers=outro_usuario["headers"])
    assert response.status_code == 200
    assert artigo["id"] in [a["id"] for a in response.json()]


async def test_obter_artigo_por_id(client: AsyncClient, usuario: dict, artigo: dict):
    response = await client.get(
        f"{BASE_URL}/{artigo['id']}", headers=usuario["headers"]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == artigo["id"]
    assert data["titulo"] == artigo["titulo"]
    assert data["usuario_id"] == usuario["id"]


async def test_obter_artigo_inexistente(client: AsyncClient, usuario: dict):
    response = await client.get(
        f"{BASE_URL}/{ID_INEXISTENTE}", headers=usuario["headers"]
    )
    assert response.status_code == 404


# --------------------------------------------------------------------------- #
# Atualizar
# --------------------------------------------------------------------------- #
async def test_atualizar_artigo(client: AsyncClient, usuario: dict, artigo: dict):
    payload = _payload_artigo(
        usuario["id"],
        titulo="Título Atualizado",
        url_fonte="https://example.com/novo",
        descricao="Nova descrição",
    )
    response = await client.put(
        f"{BASE_URL}/{artigo['id']}", json=payload, headers=usuario["headers"]
    )
    assert response.status_code == 202
    data = response.json()
    assert data["id"] == artigo["id"]
    assert data["titulo"] == "Título Atualizado"
    assert data["url_fonte"] == "https://example.com/novo"
    assert data["descricao"] == "Nova descrição"


async def test_atualizar_artigo_nao_muda_autor(
    client: AsyncClient, usuario: dict, outro_usuario: dict, artigo: dict
):
    payload = _payload_artigo(outro_usuario["id"], titulo="Tentando trocar o autor")
    response = await client.put(
        f"{BASE_URL}/{artigo['id']}", json=payload, headers=usuario["headers"]
    )
    assert response.status_code == 202
    assert response.json()["usuario_id"] == usuario["id"]


async def test_atualizar_artigo_de_outro_usuario_proibido(
    client: AsyncClient, outro_usuario: dict, artigo: dict
):
    payload = _payload_artigo(outro_usuario["id"], titulo="Invasor")
    response = await client.put(
        f"{BASE_URL}/{artigo['id']}", json=payload, headers=outro_usuario["headers"]
    )
    assert response.status_code == 403

    # o artigo permanece inalterado
    check = await client.get(
        f"{BASE_URL}/{artigo['id']}", headers=outro_usuario["headers"]
    )
    assert check.json()["titulo"] == artigo["titulo"]


async def test_admin_atualiza_artigo_de_outro_usuario(
    client: AsyncClient, admin: dict, artigo: dict
):
    payload = _payload_artigo(admin["id"], titulo="Editado pelo Admin")
    response = await client.put(
        f"{BASE_URL}/{artigo['id']}", json=payload, headers=admin["headers"]
    )
    assert response.status_code == 202
    assert response.json()["titulo"] == "Editado pelo Admin"


async def test_atualizar_artigo_inexistente(client: AsyncClient, usuario: dict):
    response = await client.put(
        f"{BASE_URL}/{ID_INEXISTENTE}",
        json=_payload_artigo(usuario["id"]),
        headers=usuario["headers"],
    )
    assert response.status_code == 404


async def test_atualizar_artigo_payload_invalido(
    client: AsyncClient, usuario: dict, artigo: dict
):
    response = await client.put(
        f"{BASE_URL}/{artigo['id']}",
        json={"titulo": "Incompleto"},
        headers=usuario["headers"],
    )
    assert response.status_code == 422


# --------------------------------------------------------------------------- #
# Deletar
# --------------------------------------------------------------------------- #
async def test_deletar_artigo(client: AsyncClient, usuario: dict, artigo: dict):
    response = await client.delete(
        f"{BASE_URL}/{artigo['id']}", headers=usuario["headers"]
    )
    assert response.status_code == 204

    check = await client.get(f"{BASE_URL}/{artigo['id']}", headers=usuario["headers"])
    assert check.status_code == 404


async def test_deletar_artigo_de_outro_usuario_proibido(
    client: AsyncClient, usuario: dict, outro_usuario: dict, artigo: dict
):
    response = await client.delete(
        f"{BASE_URL}/{artigo['id']}", headers=outro_usuario["headers"]
    )
    assert response.status_code == 403

    # continua existindo
    check = await client.get(f"{BASE_URL}/{artigo['id']}", headers=usuario["headers"])
    assert check.status_code == 200


async def test_admin_deleta_artigo_de_outro_usuario(
    client: AsyncClient, admin: dict, artigo: dict
):
    response = await client.delete(
        f"{BASE_URL}/{artigo['id']}", headers=admin["headers"]
    )
    assert response.status_code == 204

    check = await client.get(f"{BASE_URL}/{artigo['id']}", headers=admin["headers"])
    assert check.status_code == 404


async def test_deletar_artigo_inexistente(client: AsyncClient, usuario: dict):
    response = await client.delete(
        f"{BASE_URL}/{ID_INEXISTENTE}", headers=usuario["headers"]
    )
    assert response.status_code == 404