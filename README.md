# Estudo de APIs Assíncronas com FastAPI e SQLAlchemy

Repositório de estudo focado nos fundamentos de desenvolvimento de APIs RESTful em Python utilizando **FastAPI**, **SQLAlchemy 2.0 (Async)**, **Pydantic v2** e **PostgreSQL 16**.

O objetivo do projeto é praticar a construção de um CRUD completo, aplicando conceitos de programação assíncrona, organização modular de código, containerização do banco de dados e testes automatizados.

---

## 🎯 Conceitos Praticados

* **Operações Assíncronas:** Uso de `AsyncSession` (SQLAlchemy 2.0) e do driver `asyncpg` para comunicação não bloqueante com o PostgreSQL.
* **Estruturação em Camadas:** Separação entre configurações (`core/`), modelos de banco (`models/`), validação de entrada e saída (`schemas/`) e rotas (`api/v1/`).
* **Validação de Dados:** Tipagem estrita e serialização automática com Pydantic v2 (`ConfigDict`).
* **Variáveis de Ambiente:** Gerenciamento de configurações e credenciais via `.env` e `pydantic-settings`.
* **Containerização:** Uso do Docker Compose para subir o banco de dados PostgreSQL isolado em ambiente de desenvolvimento.
* **Testes e CI:** Escrita de testes de integração nas rotas com `pytest` e `httpx`, executados automaticamente via GitHub Actions.

---

## 🗂️ Estrutura de Pastas

```text
fastAPI_udemy/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de validação do Docker e execução dos testes
├── api/
│   └── v1/
│       ├── endpoints/
│       │   └── cursos.py        # Rotas CRUD (GET, POST, PUT, DELETE)
│       └── api.py               # Roteador principal da versão 1
├── core/
│   ├── config.py                # Leitura das variáveis de ambiente
│   ├── database.py              # Configuração da engine e sessão assíncrona
│   └── deps.py                  # Injeção de dependência da sessão do banco
├── models/
│   ├── __all_models.py          # Importação central dos modelos ORM
│   └── models_curso.py          # Definição da tabela "cursos"
├── schemas/
│   └── curso_schema.py          # Schemas Pydantic para validação de dados
├── tests/
│   ├── conftest.py              # Setup do banco de teste e cliente HTTP assíncrono
│   └── test_cursos.py           # Testes das operações CRUD
├── .env_exemplo                 # Modelo de variáveis de ambiente
├── docker-compose.yml           # Definição do container PostgreSQL 16
├── criar_tabelas.py             # Script para criar as tabelas no banco
├── main.py                      # Inicialização da aplicação FastAPI
├── pytest.ini                   # Configuração do Pytest
└── requirements.txt             # Dependências do projeto

