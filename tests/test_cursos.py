import pytest
from httpx import AsyncClient
from core.config import settings

BASE_URL = f"{settings.API_V1_STR}/cursos"


@pytest.mark.asyncio
async def test_criar_curso(client: AsyncClient):
    payload = {
        "titulo": "FastAPI com SQLAlchemy Async",
        "aulas": 30,
        "horas": 15
    }
    response = await client.post(f"{BASE_URL}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == payload["titulo"]
    assert data["aulas"] == payload["aulas"]
    assert data["horas"] == payload["horas"]
    assert "id" in data


@pytest.mark.asyncio
async def test_listar_cursos(client: AsyncClient):
    response = await client.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_obter_curso_por_id(client: AsyncClient):
    response = await client.get(f"{BASE_URL}/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["titulo"] == "FastAPI com SQLAlchemy Async"


@pytest.mark.asyncio
async def test_atualizar_curso(client: AsyncClient):
    payload_atualizado = {
        "titulo": "FastAPI Avançado",
        "aulas": 45,
        "horas": 22
    }
    response = await client.put(f"{BASE_URL}/1", json=payload_atualizado)
    assert response.status_code == 202
    data = response.json()
    assert data["titulo"] == "FastAPI Avançado"
    assert data["aulas"] == 45


@pytest.mark.asyncio
async def test_deletar_curso(client: AsyncClient):
    response = await client.delete(f"{BASE_URL}/1")
    assert response.status_code == 204

    response_get = await client.get(f"{BASE_URL}/1")
    assert response_get.status_code == 404