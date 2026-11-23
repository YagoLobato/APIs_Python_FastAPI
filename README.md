# Estudo de APIs Assíncronas com FastAPI e SQLAlchemy
 
Repositório de estudo focado nos fundamentos de desenvolvimento de APIs RESTful em Python utilizando **FastAPI**, **SQLAlchemy 2.0 (Async)**, **Pydantic v2** e **PostgreSQL 16**.
 
O objetivo do projeto é praticar a construção de CRUDs completos, aplicando conceitos de programação assíncrona, autenticação com JWT, relacionamento entre tabelas, organização modular de código, containerização do banco de dados e testes automatizados.
 
---
 
## 🎯 Conceitos Praticados
 
* **Operações Assíncronas:** Uso de `AsyncSession` (SQLAlchemy 2.0) e do driver `asyncpg` para comunicação não bloqueante com o PostgreSQL.
* **Estruturação em Camadas:** Separação entre configurações (`core/`), modelos de banco (`models/`), validação de entrada e saída (`schemas/`) e rotas (`api/v1/`).
* **Relacionamento entre Tabelas:** Relação um-para-muitos entre usuários e artigos (`relationship`, `ForeignKey`, `selectin` para carregamento em contexto assíncrono e `cascade` para remoção em cadeia).
* **Autenticação com JWT:** Login via `OAuth2PasswordBearer`, geração e validação de tokens com `python-jose` e rotas protegidas por dependência (`get_usuario_logado`).
* **Segurança de Senhas:** Hash de senhas com `passlib` + `bcrypt`, e schemas separados para que o hash nunca seja devolvido nas respostas da API.
* **Controle de Permissões:** Regras de autorização por dono do recurso ou administrador (usuário só altera o que é seu; `eh_admin` só pode ser alterado por um admin).
* **Validação de Dados:** Tipagem estrita e serialização automática com Pydantic v2 (`ConfigDict`, `EmailStr`).
* **Variáveis de Ambiente:** Gerenciamento de configurações e credenciais (incluindo a chave do JWT) via `.env` e `pydantic-settings`.
* **Containerização:** Uso do Docker Compose para subir o banco de dados PostgreSQL isolado em ambiente de desenvolvimento, e de um segundo banco descartável (em memória) só para os testes.
* **Testes e CI:** Escrita de testes de integração nas rotas com `pytest` e `httpx`, independentes entre si (cada teste cria os próprios dados), executados automaticamente via GitHub Actions.
---
 
## 🔌 Endpoints
 
Todos os caminhos ficam sob o prefixo `/api/v1`. A documentação interativa (Swagger) fica disponível em `/docs`.
 
### Usuários (`/usuarios`)
 
| Método | Rota | Acesso | Descrição |
| --- | --- | --- | --- |
| `POST` | `/signup` | Público | Cria um usuário (nunca cria admin) |
| `POST` | `/login` | Público | Autentica e devolve o token JWT |
| `GET` | `/logado` | Logado | Retorna o usuário do token |
| `GET` | `/` | Logado | Lista os usuários |
| `GET` | `/{id}` | Logado | Retorna um usuário com seus artigos |
| `PUT` | `/{id}` | Próprio usuário ou admin | Atualiza dados (parcial) |
| `DELETE` | `/{id}` | Próprio usuário ou admin | Remove o usuário e seus artigos |
 
### Artigos (`/artigos`)
 
| Método | Rota | Acesso | Descrição |
| --- | --- | --- | --- |
| `GET` | `/` | Logado | Lista os artigos |
| `POST` | `/` | Logado | Cria um artigo (o autor é sempre o usuário logado) |
| `GET` | `/{id}` | Logado | Retorna um artigo |
| `PUT` | `/{id}` | Autor ou admin | Atualiza o artigo (o autor não muda) |
| `DELETE` | `/{id}` | Autor ou admin | Remove o artigo |
 
### Cursos (`/cursos`)
 
CRUD simples (`GET`, `POST`, `PUT`, `DELETE`), usado como primeiro exercício do projeto.
 
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
│       │   ├── artigos.py       # Rotas CRUD de artigos (protegidas)
│       │   ├── cursos.py        # Rotas CRUD de cursos
│       │   └── usuarios.py      # Signup, login e CRUD de usuários
│       └── api.py               # Roteador principal da versão 1
├── core/
│   ├── auth.py                  # Autenticação do usuário e criação do token JWT
│   ├── config.py                # Leitura das variáveis de ambiente
│   ├── database.py              # Configuração da engine e sessão assíncrona
│   ├── deps.py                  # Dependências: sessão do banco e usuário logado
│   └── security.py              # Hash e verificação de senhas (bcrypt)
├── models/
│   ├── __all_models.py          # Importação central dos modelos ORM
│   ├── models_artigos.py        # Definição da tabela "artigos"
│   ├── models_curso.py          # Definição da tabela "cursos"
│   └── models_usuarios.py       # Definição da tabela "usuarios"
├── schemas/
│   ├── artigos_schema.py        # Schemas Pydantic de artigos
│   ├── curso_schema.py          # Schemas Pydantic de cursos
│   └── usuarios_schema.py       # Schemas Pydantic de usuários (base, create, update, com artigos)
├── tests/
│   ├── conftest.py              # Cliente HTTP assíncrono e criação/remoção das tabelas de teste
│   ├── test_artigos.py          # Testes do CRUD e das permissões de artigos
│   ├── test_cursos.py           # Testes das operações CRUD de cursos
│   └── test_usuarios.py         # Testes de signup, login, CRUD e permissões de usuários
├── .env_exemplo                 # Modelo de variáveis de ambiente
├── docker-compose.yml           # Containers PostgreSQL 16 (desenvolvimento e db_test descartável)
├── criar_tabelas.py             # Script para criar as tabelas no banco
├── main.py                      # Inicialização da aplicação FastAPI
├── pytest.ini                   # Configuração do Pytest
└── requirements.txt             # Dependências do projeto
```
 
---
 
## 🚀 Como Rodar
 
```bash
# 1. Criar e ativar o ambiente virtual, e instalar as dependências
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
 
# 2. Criar o .env a partir do modelo e preencher os valores
cp .env_exemplo .env
# gere uma chave segura para o JWT_SECRET_KEY com:
openssl rand -hex 32
 
# 3. Subir o banco de dados e criar as tabelas
docker compose up -d --wait
python criar_tabelas.py
 
# 4. Iniciar a API
uvicorn main:app --reload
```
 
---
 
## 🧪 Testes
 
Os testes rodam em um banco PostgreSQL descartável (`db_test`, em memória), separado do banco de desenvolvimento. As tabelas são criadas antes da execução e apagadas no final, e há uma trava de segurança que impede o `drop_all` em qualquer banco cujo nome não termine com `_test`.
 
```bash
docker compose --profile test up -d --wait db_test
python -m pytest -v
docker compose --profile test rm -sf db_test
```
 
No GitHub Actions, o mesmo fluxo roda a cada Pull Request e push para a `main`, com um serviço PostgreSQL próprio do pipeline.
 