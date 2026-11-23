"""Testes dos endpoints de usuários.

Requisitos:
  - fixture `client` (httpx.AsyncClient apontando para o app, com banco de testes) no conftest.py
  - pytest e pytest-asyncio

Cada teste cria os próprios dados (e-mails únicos), então não depende da ordem
de execução nem de dados já existentes no banco.
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

BASE_URL = f"{settings.API_V1_STR}/usuarios"
ARTIGOS_URL = f"{settings.API_V1_STR}/artigos"
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
    response = await client.post(f"{BASE_URL}/signup", json=dados)
    assert response.status_code == 201, response.text
    return {**dados, "id": response.json()["id"]}


async def _login(client: AsyncClient, email: str, senha: str = SENHA_PADRAO) -> dict:
    response = await client.post(
        f"{BASE_URL}/login", data={"username": email, "password": senha}
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


# --------------------------------------------------------------------------- #
# Proteção das rotas
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "metodo, caminho",
    [
        ("GET", "/logado"),
        ("GET", "/"),
        ("GET", "/1"),
        ("PUT", "/1"),
        ("DELETE", "/1"),
    ],
)
async def test_rotas_protegidas_exigem_token(client: AsyncClient, metodo, caminho):
    response = await client.request(
        metodo, f"{BASE_URL}{caminho}", json={"nome": "Qualquer"}
    )
    assert response.status_code == 401


async def test_token_invalido_retorna_401(client: AsyncClient):
    headers = {"Authorization": "Bearer token.invalido.aqui"}
    response = await client.get(f"{BASE_URL}/logado", headers=headers)
    assert response.status_code == 401


# --------------------------------------------------------------------------- #
# Signup
# --------------------------------------------------------------------------- #
async def test_signup_sucesso(client: AsyncClient):
    payload = {"nome": "Maria", "email": _email_unico(), "senha": SENHA_PADRAO}
    response = await client.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == payload["nome"]
    assert data["email"] == payload["email"]
    assert data["ativo"] is True
    assert data["eh_admin"] is False
    assert "id" in data


async def test_signup_nao_retorna_senha(client: AsyncClient):
    payload = {"nome": "Maria", "email": _email_unico(), "senha": SENHA_PADRAO}
    response = await client.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 201
    assert "senha" not in response.json()


async def test_signup_ignora_eh_admin(client: AsyncClient):
    payload = {
        "nome": "Espertinho",
        "email": _email_unico(),
        "senha": SENHA_PADRAO,
        "eh_admin": True,
    }
    response = await client.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 201
    assert response.json()["eh_admin"] is False


async def test_signup_email_duplicado(client: AsyncClient, usuario: dict):
    payload = {"nome": "Duplicado", "email": usuario["email"], "senha": SENHA_PADRAO}
    response = await client.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 406


async def test_signup_email_invalido(client: AsyncClient):
    payload = {"nome": "Sem Email", "email": "isso-nao-e-email", "senha": SENHA_PADRAO}
    response = await client.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 422


async def test_signup_campos_obrigatorios(client: AsyncClient):
    response = await client.post(f"{BASE_URL}/signup", json={"nome": "Só nome"})
    assert response.status_code == 422


# --------------------------------------------------------------------------- #
# Login
# --------------------------------------------------------------------------- #
async def test_login_sucesso(client: AsyncClient):
    dados = await _criar_usuario(client)
    response = await client.post(
        f"{BASE_URL}/login",
        data={"username": dados["email"], "password": dados["senha"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


async def test_login_senha_incorreta(client: AsyncClient, usuario: dict):
    response = await client.post(
        f"{BASE_URL}/login",
        data={"username": usuario["email"], "password": "senha-errada"},
    )
    assert response.status_code == 400


async def test_login_email_inexistente(client: AsyncClient):
    response = await client.post(
        f"{BASE_URL}/login",
        data={"username": _email_unico(), "password": SENHA_PADRAO},
    )
    assert response.status_code == 400


async def test_login_usuario_inativo(client: AsyncClient):
    dados = await _criar_usuario(client, ativo=False)
    response = await client.post(
        f"{BASE_URL}/login",
        data={"username": dados["email"], "password": dados["senha"]},
    )
    assert response.status_code == 403


# --------------------------------------------------------------------------- #
# Usuário logado
# --------------------------------------------------------------------------- #
async def test_get_usuario_logado(client: AsyncClient, usuario: dict):
    response = await client.get(f"{BASE_URL}/logado", headers=usuario["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == usuario["id"]
    assert data["email"] == usuario["email"]
    assert "senha" not in data


# --------------------------------------------------------------------------- #
# Listar / obter
# --------------------------------------------------------------------------- #
async def test_listar_usuarios(client: AsyncClient, usuario: dict):
    response = await client.get(f"{BASE_URL}/", headers=usuario["headers"])
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert usuario["id"] in [u["id"] for u in data]
    assert all("senha" not in u for u in data)


async def test_obter_usuario_por_id(client: AsyncClient, usuario: dict):
    response = await client.get(
        f"{BASE_URL}/{usuario['id']}", headers=usuario["headers"]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == usuario["id"]
    assert data["nome"] == usuario["nome"]
    assert data["artigos"] == []
    assert "senha" not in data


async def test_obter_usuario_retorna_seus_artigos(client: AsyncClient, usuario: dict):
    payload = {
        "titulo": "Artigo do usuário",
        "url_fonte": "https://example.com/a",
        "descricao": "Descrição",
        "usuario_id": usuario["id"],
    }
    criado = await client.post(
        f"{ARTIGOS_URL}/", json=payload, headers=usuario["headers"]
    )
    assert criado.status_code == 201

    response = await client.get(
        f"{BASE_URL}/{usuario['id']}", headers=usuario["headers"]
    )
    assert response.status_code == 200
    titulos = [a["titulo"] for a in response.json()["artigos"]]
    assert payload["titulo"] in titulos


async def test_obter_usuario_inexistente(client: AsyncClient, usuario: dict):
    response = await client.get(
        f"{BASE_URL}/{ID_INEXISTENTE}", headers=usuario["headers"]
    )
    assert response.status_code == 404


# --------------------------------------------------------------------------- #
# Atualizar
# --------------------------------------------------------------------------- #
async def test_atualizar_proprio_usuario(client: AsyncClient, usuario: dict):
    response = await client.put(
        f"{BASE_URL}/{usuario['id']}",
        json={"nome": "Nome Atualizado"},
        headers=usuario["headers"],
    )
    assert response.status_code == 202
    data = response.json()
    assert data["nome"] == "Nome Atualizado"
    assert data["email"] == usuario["email"]  # campo não enviado permanece igual


async def test_atualizar_senha(client: AsyncClient, usuario: dict):
    nova_senha = "NovaSenha@999"
    response = await client.put(
        f"{BASE_URL}/{usuario['id']}",
        json={"senha": nova_senha},
        headers=usuario["headers"],
    )
    assert response.status_code == 202

    login_novo = await client.post(
        f"{BASE_URL}/login",
        data={"username": usuario["email"], "password": nova_senha},
    )
    assert login_novo.status_code == 200

    login_antigo = await client.post(
        f"{BASE_URL}/login",
        data={"username": usuario["email"], "password": usuario["senha"]},
    )
    assert login_antigo.status_code == 400


async def test_atualizar_email_duplicado(
    client: AsyncClient, usuario: dict, outro_usuario: dict
):
    response = await client.put(
        f"{BASE_URL}/{usuario['id']}",
        json={"email": outro_usuario["email"]},
        headers=usuario["headers"],
    )
    assert response.status_code == 406


async def test_atualizar_outro_usuario_proibido(
    client: AsyncClient, usuario: dict, outro_usuario: dict
):
    response = await client.put(
        f"{BASE_URL}/{outro_usuario['id']}",
        json={"nome": "Invasor"},
        headers=usuario["headers"],
    )
    assert response.status_code == 403


async def test_nao_admin_nao_altera_eh_admin(client: AsyncClient, usuario: dict):
    response = await client.put(
        f"{BASE_URL}/{usuario['id']}",
        json={"eh_admin": True},
        headers=usuario["headers"],
    )
    assert response.status_code == 202
    assert response.json()["eh_admin"] is False


async def test_admin_atualiza_outro_usuario(
    client: AsyncClient, usuario: dict, admin: dict
):
    response = await client.put(
        f"{BASE_URL}/{usuario['id']}",
        json={"nome": "Editado pelo Admin"},
        headers=admin["headers"],
    )
    assert response.status_code == 202
    assert response.json()["nome"] == "Editado pelo Admin"


async def test_admin_altera_eh_admin(client: AsyncClient, usuario: dict, admin: dict):
    response = await client.put(
        f"{BASE_URL}/{usuario['id']}",
        json={"eh_admin": True},
        headers=admin["headers"],
    )
    assert response.status_code == 202
    assert response.json()["eh_admin"] is True


async def test_atualizar_usuario_inexistente(client: AsyncClient, admin: dict):
    response = await client.put(
        f"{BASE_URL}/{ID_INEXISTENTE}",
        json={"nome": "Fantasma"},
        headers=admin["headers"],
    )
    assert response.status_code == 404


# --------------------------------------------------------------------------- #
# Deletar
# --------------------------------------------------------------------------- #
async def test_deletar_proprio_usuario(client: AsyncClient, usuario: dict):
    response = await client.delete(
        f"{BASE_URL}/{usuario['id']}", headers=usuario["headers"]
    )
    assert response.status_code == 204

    login = await client.post(
        f"{BASE_URL}/login",
        data={"username": usuario["email"], "password": usuario["senha"]},
    )
    assert login.status_code == 400


async def test_deletar_outro_usuario_proibido(
    client: AsyncClient, usuario: dict, outro_usuario: dict
):
    response = await client.delete(
        f"{BASE_URL}/{outro_usuario['id']}", headers=usuario["headers"]
    )
    assert response.status_code == 403

    # continua existindo
    check = await client.get(
        f"{BASE_URL}/{outro_usuario['id']}", headers=outro_usuario["headers"]
    )
    assert check.status_code == 200


async def test_admin_deleta_outro_usuario(
    client: AsyncClient, usuario: dict, admin: dict
):
    response = await client.delete(
        f"{BASE_URL}/{usuario['id']}", headers=admin["headers"]
    )
    assert response.status_code == 204

    check = await client.get(f"{BASE_URL}/{usuario['id']}", headers=admin["headers"])
    assert check.status_code == 404


async def test_deletar_usuario_remove_seus_artigos(
    client: AsyncClient, usuario: dict, admin: dict
):
    payload = {
        "titulo": "Artigo que vai sumir",
        "url_fonte": "https://example.com/b",
        "descricao": "Descrição",
        "usuario_id": usuario["id"],
    }
    criado = await client.post(
        f"{ARTIGOS_URL}/", json=payload, headers=usuario["headers"]
    )
    assert criado.status_code == 201
    artigo_id = criado.json()["id"]

    response = await client.delete(
        f"{BASE_URL}/{usuario['id']}", headers=admin["headers"]
    )
    assert response.status_code == 204

    check = await client.get(f"{ARTIGOS_URL}/{artigo_id}", headers=admin["headers"])
    assert check.status_code == 404


async def test_deletar_usuario_inexistente(client: AsyncClient, admin: dict):
    response = await client.delete(
        f"{BASE_URL}/{ID_INEXISTENTE}", headers=admin["headers"]
    )
    assert response.status_code == 404