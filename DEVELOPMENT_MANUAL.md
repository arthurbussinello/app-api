# Manual de Desenvolvimento — api-ia

## Visão Geral do Projeto

**api-ia** é uma *API corporativa de inteligência artificial* construída com **FastAPI**. O projeto foi projetado como um *esqueleto funcional* (skeleton) que abstrai a complexidade de integração com provedores de IA, agentes autônomos, ferramentas e persistência de dados.

O objetivo principal é fornecer uma base modular onde você possa inserir funcionalidades reais (chamadas a LLMs externos, integrações com sistemas externos, persistência em banco de dados) sem precisar reestruturar a arquitetura existente.

---

## 🗺️ Estrutura do Projeto

```
api_ia/
├── main.py                          # Entry point — configura FastAPI, middlewares, routers
├── app/
│   ├── config.py                    # Configurações via variáveis de ambiente (.env)
│   ├── main.py                      # Configuração principal (logging, exceções)
│   │
│   ├── providers/                   # Camada de comunicação com IA
│   │   ├── base.py                  # BaseProvider (ABC — contrato mínimo)
│   │   ├── local_provider.py        # Provider mock local (sem API externa)
│   │   ├── online_provider.py       # Provider simulado para APIs externas (OpenAI-style)
│   │   ├── corporate_provider.py    # Provider simulado para gateway corporativo
│   │   └── router.py                # ProviderRouter — roteamento e registro de providers
│   │
│   ├── agents/                      # Camada de agentes autônomos
│   │   ├── base.py                  # BaseAgent (ABC — contrato mínimo)
│   │   ├── runner.py                # AgentRunner — loop de execução com limite de iterações
│   │   ├── prompts.py               # Prompts fixos para agentes
│   │   └── research_agent.py        # Exemplo de agente: ResearchAgent
│   │
│   ├── agents/tools/                # Ferramentas que agentes utilizam
│   │   └── base.py                  # BaseTool + SQLReadOnlyTool + TOOL_REGISTRY
│   │
│   ├── services/                    # Camada de negócio (orchestration)
│   │   ├── chat_service.py          # ChatService — orquestra chamadas ao provider
│   │   ├── agent_service.py         # AgentService — orquestra execução de agentes
│   │   ├── session_service.py       # SessionService — gerencia sessões em memória
│   │   └── audit_service.py         # AuditService — registro de operações
│   │
│   ├── repositories/                # Camada de dados (preparado para persistência)
│   │   ├── message_repository.py    # MessageRepository — mensagens simuladas
│   │   ├── audit_repository.py      # AuditRepository — registros simulados
│   │   └── request_repository.py    # RequestRepository — requisições simuladas
│   │
│   ├── schemas/                     # Schemas Pydantic (validação de requests/responses)
│   │   ├── common.py                # ApiResponse, ErrorResponse
│   │   ├── chat.py                  # ChatMessage, ChatResponse
│   │   ├── agents.py                # AgentRunRequest, AgentRunResponse
│   │   └── tools.py                 # ToolInfo, ToolCallRequest, ToolCallResponse
│   │
│   ├── sql/                         # Validação e registro SQL
│   │   ├── validators.py            # validate_sql — bloqueia comandos perigosos (apenas SELECT)
│   │   └── registry.py              # Registro de tabelas/columnas
│   │
│   ├── core/                        # Utilitários fundamentais
│   │   ├── exceptions.py            # ProviderError, AgentError, SQLValidationError...
│   │   ├── security.py              # Funções de segurança (auth, tokens)
│   │   ├── permissions.py           # Controle de permissões
│   │   └── logging_config.py        # Configuração de logs
│   │
│   ├── api/v1/                      # Rotas HTTP da API
│   │   ├── health_routes.py         # GET /health, GET /v1/health
│   │   ├── provider_routes.py       # GET /v1/providers
│   │   ├── chat_routes.py           # POST /v1/chat/completions
│   │   ├── agent_routes.py          # POST /v1/agents/{agent_id}/run
│   │   └── tools_routes.py          # GET /v1/tools, POST /v1/tools/{name}/execute
│   │
│   └── dependencies.py              # Dependências Pydantic (injectáveis)
│
├── tests/                           # Testes
├── requirements.txt                 # Dependências
├── pyproject.toml                   # Configuração do projeto
├── .env.example                     # Template de variáveis de ambiente
└── README.md
```

---

## 🏗️ Arquitetura e Padrões

### 1. Camadas da API

A arquitetura segue o padrão **Service-Repository** com três camadas principais:

```
Request (Rotas HTTP)
    ↓
Service (Orquestração de negócio)
    ↓
Provider / Agent / Tool (Execução real)
```

Cada camada tem um **contrato bem definido** via classes abstratas (`ABC`) e schemas Pydantic.

### 2. Injeção de Dependência (sutil)

A aplicação cria instâncias globais nos módulos de serviço e rotas:
- `ChatService(router=ProviderRouter())` em `chat_routes.py`
- `AgentService(runner=AgentRunner(max_iterations=5))` em `agent_routes.py`

Para ambientes de produção, recomenda-se usar FastAPI `dependencies` para injetar essas instâncias.

### 3. Provider Router Pattern

O `ProviderRouter` é um **padrão de estratégia** que permite trocar o provedor de IA sem alterar código nas rotas:

```python
router = ProviderRouter(default_provider="local")
provider = router.get_provider("online")  # troca dinâmica
```

---

## 📍 GUIA DE DESENVOLVIMENTO

---

### 🅰. Criando/Integrando um Provedor de IA Específico

#### Onde criar: `app/providers/`

**Opção A — Novo arquivo de provider (recomendado)**

```
app/providers/
├── my_provider.py          # ← Crie aqui
└── router.py               # Registre neste arquivo
```

#### Passo 1: Crie o arquivo do provider

Crie `app/providers/my_provider.py`:

```python
"""Provider para OpenAI (ChatGPT)."""

import logging
import httpx

from app.providers.base import BaseProvider
from app.config import settings

logger = logging.getLogger("ia_api.providers.openai")


class OpenAIProvider(BaseProvider):
    """Provider que se conecta à API OpenAI."""

    @property
    def provider_id(self) -> str:
        return "openai"

    def _is_available(self) -> bool:
        return settings.provider_online_enabled  # ou crie uma flag específica

    def complete(self, prompt: str, **kwargs) -> dict:
        if not self._is_available():
            raise ConnectionError("OpenAI provider is disabled")
        
        # Implementação real com OpenAI SDK ou httpx
        from openai import OpenAI
        client = OpenAI(api_key=settings.provider_online_api_key)
        
        response = client.chat.completions.create(
            model=kwargs.get("model", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
        )
        
        return {
            "message": {
                "role": "assistant",
                "content": response.choices[0].message.content,
            }
        }

    def chat(self, messages: list[dict], **kwargs) -> dict:
        if not self._is_available():
            raise ConnectionError("OpenAI provider is disabled")
        
        from openai import OpenAI
        client = OpenAI(api_key=settings.provider_online_api_key)
        
        response = client.chat.completions.create(
            model=kwargs.get("model", "gpt-3.5-turbo"),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
        )
        
        return {
            "message": {
                "role": "assistant",
                "content": response.choices[0].message.content,
            }
        }
```

#### Passo 2: Registre no Router

Em `app/providers/router.py`, adicione ao método `_register_defaults`:

```python
from app.providers.my_provider import OpenAIProvider  # ← Importe

def _register_defaults(self) -> None:
    # ... registros existentes ...
    
    openai = OpenAIProvider()
    self._providers[openai.provider_id] = openai
    logger.info("Registered provider: %s", openai.provider_id)
```

#### Passo 3: Habilite no `.env`

```env
PROVIDER_ONLINE_ENABLED=true
PROVIDER_ONLINE_API_KEY="sk-sua-chave-api"
```

#### Funções afetadas pela adição de um provider:

| Camada | Arquivo | Impacto |
|--------|---------|---------|
| Rotas | `app/api/v1/chat_routes.py` | Nenhuma — usa `router.get_provider()` |
| Serviço | `app/services/chat_service.py` | Nenhona — chama `prov.chat()` |
| Router | `app/providers/router.py` | Registro do novo provider |

---

### 🅱. Criando Tools que Conversam com Outro Projeto

#### Onde criar: `app/agents/tools/`

As ferramentas são **classes que seguem o contrato** `BaseTool`:

```python
class BaseTool(ABC):
    @property
    def tool_name(self) -> str: ...
    
    @property
    def tool_description(self) -> str: ...
    
    @abstractmethod
    def execute(self, arguments: dict) -> str: ...
```

#### Exemplo: Tool que consome API externa de outro projeto

Crie `app/agents/tools/web_scraper.py`:

```python
import httpx
from app.agents.tools.base import BaseTool


class WebScraperTool(BaseTool):
    """Ferramenta para buscar dados via API externa."""

    @property
    def tool_name(self) -> str:
        return "web_scraper"

    @property
    def tool_description(self) -> str:
        return (
            "Busca dados de uma API externa. "
            "Recebe 'url' e 'method' como argumentos."
        )

    def execute(self, arguments: dict) -> str:
        url = arguments.get("url")
        method = arguments.get("method", "GET")
        
        if not url:
            return "Erro: url não fornecida"
        
        try:
            response = httpx.request(method, url)
            response.raise_for_status()
            data = response.json()
            return f"Sucesso:\n{data}"
        except Exception as e:
            return f"Erro na requisição: {str(e)}"
```

#### Como registrar e usar:

**1. Registre no `app/agents/tools/base.py`:**

```python
from app.agents.tools.web_scraper import WebScraperTool

TOOL_REGISTRY = {
    "sql_readonly": SQLReadOnlyTool(),
    "web_scraper": WebScraperTool(),  # ← Adicione aqui
}
```

**2. O agente pode usar automaticamente** — o `ResearchAgent` já lista e executa ferramentas pelo nome:

```python
# No research_agent.py, o fluxo é:
tool = get_tool("web_scraper")  # Já funciona!
result = tool.execute({"url": "https://outro-projeto/api/dados"})
```

**3. Via API HTTP:**

```bash
curl -X POST "http://localhost:8000/v1/tools/web_scraper/execute" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://outro-projeto/api/dados", "method": "GET"}'
```

#### Padrão de comunicação recomendado para projetos externos:

| Tipo | Protocolo | Formato | Tool Exemplo |
|------|-----------|---------|--------------|
| REST API | HTTP/HTTPS | JSON | `WebScraperTool` |
| GraphQL | HTTP | GraphQL Query | `GraphQLQueryTool` |
| Mensageria | RabbitMQ/Kafka | JSON/Mensagem | `MessageQueueTool` |
| Banco de dados | TCP (driver) | SQL/Driver | `SQLReadOnlyTool` |

---

### 🅲. Persistência de Chat em Banco de Dados

A estrutura **já possui repositórios preparados** para persistência. Aqui está o que precisa ser alterado:

#### 1. Configuração do Banco (`app/config.py`)

Já existem configurações para SQL Server. Para escrita (chat), adicione ao `.env`:

```env
CHAT_DB_HOST=localhost
CHAT_DB_PORT=5432
CHAT_DB_NAME=chat_db
CHAT_DB_USER=chat_user
CHAT_DB_PASSWORD=chat_password
```

#### 2. Implementar o Repository (`app/repositories/message_repository.py`)

Atualmente é **mock (em memória)**. Para persistência real:

```python
# app/repositories/message_repository.py

import logging
from datetime import UTC, datetime
import asyncpg  # ou sqlalchemy, pyodbc

logger = logging.getLogger("ia_api.message_repository")


class MessageRepository:
    """Repositório de mensagens com persistência em PostgreSQL."""

    def __init__(self):
        self._pool = None  # connection pool

    async def init(self, dsn: str):
        """Inicializa conexão com o banco."""
        self._pool = await asyncpg.create_pool(dsn)
        logger.info("MessageRepository connected to database")

    async def save(self, session_id: str, role: str, content: str, 
                   provider: str = "local", model: str = "mock") -> dict:
        """Salva uma mensagem no chat com persistência real."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO chat_messages (session_id, role, content, provider, model, created_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
                RETURNING id, session_id, role, content, provider, model, created_at
                """,
                session_id, role, content, provider, model
            )
        logger.info("Message persisted: #%d session=%s", row['id'], session_id)
        return dict(row)

    async def find_by_session(self, session_id: str, limit: int = 100) -> list[dict]:
        """Retorna mensagens persistidas de uma sessão."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM chat_messages WHERE session_id = $1 ORDER BY id DESC LIMIT $2",
                session_id, limit
            )
        return [dict(r) for r in rows]

    def get_connection(self):
        """Retorna pool para queries customizadas."""
        return self._pool
```

#### 3. Criar SQL Schema (`app/sql/schema.sql` — novo arquivo)

```sql
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    provider VARCHAR(32),
    model VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) REFERENCES chat_sessions(session_id),
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    provider VARCHAR(32),
    model VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON chat_messages(session_id);
```

#### 4. Integrar com Service (`app/services/chat_service.py`)

No método `complete()`, **adicione persistência após a resposta**:

```python
# Em app/services/chat_service.py — no __init__:

def __init__(self, router: ProviderRouter, message_repo=None):
    self.router = router
    self.message_repo = message_repo  # ← Repository com DB real

def complete(self, messages, provider=None, model=None, temperature=None):
    prov = self.router.get_provider(provider)
    result = prov.chat(messages)
    response_msg = result.get("message", {})

    # ← ADICIONE: persistir após resposta
    if self.message_repo:
        session_id = f"session_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        # Persiste todas as mensagens de input + resposta
        for msg in messages:
            self.message_repo.save_sync(session_id, msg['role'], msg['content'])
        self.message_repo.save_sync(session_id, "assistant", response_msg.get('content', ''))

    return { ... }
```

#### 5. Funções Afetadas pela Persistência

| Camada | Arquivo | Alteração Necessária |
|--------|---------|---------------------|
| **Routes** | `app/api/v1/chat_routes.py` | Injetar `message_repo` via dependency |
| **Service** | `app/services/chat_service.py` | Chamar `repo.save()` após resposta |
| **Repository** | `app/repositories/message_repository.py` | Implementar com driver SQL real |
| **Config** | `app/config.py` | Adicionar conn. DB de escrita |
| **SQL** | Novo: `sql/schema.sql` | Criar tabelas |
| **Session** | `app/services/session_service.py` | Trocar memória → DB |

#### 6. Alternativa: Usar SQLAlchemy (ORM)

Crie `app/database.py`:

```python
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import UTC, datetime

Base = declarative_base()


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), unique=True, nullable=False)
    provider = Column(String(32))
    model = Column(String(64))
    created_at = Column(DateTime, default=datetime.now(UTC))


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), nullable=False)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))


engine = create_engine(settings.chat_db_url)
SessionLocal = sessionmaker(bind=engine)
```

---

### 🅳. Outras Conexões e Abstrações no Ambiente Fechado

#### 1. **Agentes Personalizados**

Para criar um novo agente, crie `app/agents/my_custom_agent.py`:

```python
from app.agents.base import BaseAgent
from app.providers.router import ProviderRouter


class MyCustomAgent(BaseAgent):
    
    @property
    def agent_id(self) -> str:
        return "my_custom"

    @property
    def agent_name(self) -> str:
        return "My Custom Agent"

    def run(self, input_data: str, params: dict = None) -> dict:
        # Use um provider para obter resposta
        router = ProviderRouter()
        provider = router.get_provider("online")
        
        response = provider.chat([
            {"role": "user", "content": input_data}
        ])
        
        return {
            "output": response["message"]["content"],
            "_done": True,
            "metadata": {"agent": self.agent_id}
        }
```

Registre no `AgentService._agents` (`app/services/agent_service.py`):

```python
from app.agents.my_custom_agent import MyCustomAgent

self._agents = {
    "research": ResearchAgent(),
    "my_custom": MyCustomAgent(),  # ← Adicione aqui
}
```

#### 2. **Permissões e Segurança** (`app/core/`)

| Arquivo | Função | Uso |
|---------|--------|-----|
| `security.py` | Autenticação (JWT, API keys) | Proteger rotas com `@router.post(..., dependencies=[Depends(get_current_user)])` |
| `permissions.py` | Controle de acesso por papel/role | Verificar se usuário pode usar determinado provider/agente |

#### 3. **Logging e Auditoria** (`app/core/logging_config.py`, `app/services/audit_service.py`)

O sistema já registra:
- Requisições ao health endpoint
- Chamadas a providers (log de input/output)
- Execuções de agentes
- Consultas SQL (validação)

Para expandir, adicione ao `AuditService`:
```python
audit.log_chat(provider="openai", messages_count=5, response_time_ms=1200)
audit.log_agent_run(agent_id="research", iterations=3, success=True)
audit.log_sql_query("SELECT * FROM usuarios", validated=True)
```

#### 4. **Session Service para Persistência de Conversa**

Atualmente `SessionService` usa memória (`dict`). Para persistência:

```python
# app/services/session_service.py — altere:

from sqlalchemy.orm import Session as DBSession
from app.database import ChatSession, ChatMessage

def create_session(self, session_id=None) -> dict:
    # Em vez de self._sessions[sid] = {...}
    db_session = ChatSession(session_id=sid, provider="local")
    self.db.add(db_session)
    self.db.commit()
```

#### 5. **Extensão de Schemas Pydantic**

Para adicionar campos a requests/responses existentes:

```python
# app/schemas/chat.py — expanda ChatResponse

class ChatResponse(BaseModel):
    id: str = ""
    created_at: str = ...
    provider: str = "local"
    model: str = "mock"
    message: dict = {}
    usage: dict = {"prompt_tokens": 0, "completion_tokens": 0}
    
    # ← Adicione:
    session_id: str | None = None
    cost_usd: float | None = None
    latency_ms: float | None = None
```

---

## 📋 Fluxo de Desenvolvimento Recomendado

### Começando a desenvolver:

1. **Defina o provider real** → `app/providers/` + `.env`
2. **Teste via curl/Swagger** → `http://localhost:8000/docs`
3. **Crie agentes personalizados** → `app/agents/`
4. **Adicione tools externas** → `app/agents/tools/`
5. **Implemente persistência** → `app/repositories/` + SQL schema
6. **Adicione autenticação** → `app/core/security.py`

### Pontos de extensão (extensibility points):

| Camada | Arquivo para Estender | Método/Classe |
|--------|----------------------|---------------|
| Provider | `app/providers/{name}_provider.py` | `complete()`, `chat()` |
| Agente | `app/agents/{name}_agent.py` | `run(input_data, params)` |
| Tool | `app/agents/tools/{name}.py` | `execute(arguments)` |
| Service | `app/services/{name}_service.py` | Métodos de orquestração |
| Repository | `app/repositories/{name}_repository.py` | CRUD methods |
| Route | `app/api/v1/{name}_routes.py` | Endpoints HTTP |
| Schema | `app/schemas/{name}.py` | Modelos Pydantic |

---

## 🔌 API Endpoints Disponíveis

| Método | Endpoint | Função |
|--------|----------|--------|
| GET | `/health` | Health check básico |
| GET | `/v1/health` | Health check v1 |
| GET | `/v1/providers` | Lista providers disponíveis |
| POST | `/v1/chat/completions` | Chat estilo OpenAI |
| POST | `/v1/agents/{id}/run` | Executa agente sem input |
| POST | `/v1/agents/{id}/run-with-input` | Executa agente com input |
| GET | `/v1/tools` | Lista ferramentas |
| POST | `/v1/tools/{name}/execute` | Executa ferramenta |

---

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Teste de rotas específicas
python -m pytest tests/test_api_routes.py -v
python -m pytest tests/test_providers.py -v
python -m pytest tests/test_services.py -v
```

---

## 📊 Diagrama de Fluxo de Dados

```
Cliente HTTP
    ↓
FastAPI Router (app/api/v1/)
    ↓
Service Layer (app/services/)
    ├── ChatService → ProviderRouter → Provider (local/online/corporate)
    ├── AgentService → AgentRunner → BaseAgent (research/custom)
    └── SessionService/AuditService
    ↓
Repository Layer (app/repositories/)
    └── MessageRepository / AuditRepository
```

---

## 🔐 Segurança e Validações

### SQL Validation (`app/sql/validators.py`)

O sistema **bloqueia** comandos SQL perigosos:
- INSERT, UPDATE, DELETE
- DROP, ALTER, CREATE
- EXEC, TRUNCATE
- Comentários (`--`, `/* */`)

Apenas **SELECT** é permitido. Isso protege contra injeção SQL quando tools executam queries.

### Custom Exceptions (`app/core/exceptions.py`)

| Exceção | Uso |
|---------|-----|
| `ProviderError` | Falha ao comunicar com provider de IA |
| `AgentError` | Falha na execução de agente |
| `SQLValidationError` | Query SQL não aprovou validação |
| `ToolError` | Falha ao executar ferramenta |
| `NotFoundError` | Recurso não encontrado |

---

## 📝 Prompts dos Agentes (`app/agents/prompts.py`)

```python
SYSTEM_PROMPT = (
    "Você é um assistente de IA corporativo. Responda de forma clara e objetiva."
)

RESEARCH_AGENT_PROMPT = (
    "Você é um agente de pesquisa. Analise o input do usuário, utilize ferramentas disponíveis "
    "para coletar informações e retorne um resumo estruturado."
)
```

Para adicionar novos agentes com prompts personalizados, crie constantes no mesmo arquivo ou importe prompts específicos para cada agente.

---

## 🚀 Como Começar a Desenvolver

### Passo a passo para primeira extensão:

1. **Escolha o tipo de extensão** (provider, agent, tool, persistence)
2. **Crie o arquivo** seguindo o padrão do diretório
3. **Herde da classe base abstrata** correspondente
4. **Implemente os métodos obrigatórios**
5. **Registre no registry/router/appropriado**
6. **Teste via Swagger**: `http://localhost:8000/docs`

### Exemplo rápido: Primeira Tool Customizada

```bash
# 1. Crie o arquivo
touch app/agents/tools/my_tool.py
```

```python
# 2. Conteúdo do my_tool.py
from app.agents.tools.base import BaseTool, get_tool

class MyCustomTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "my_custom"
    
    @property
    def tool_description(self) -> str:
        return "Minha ferramenta customizada"
    
    def execute(self, arguments: dict) -> str:
        param = arguments.get("param", "")
        return f"Resultado: {param}"

# Registre automaticamente ao importar
TOOL_REGISTRY["my_custom"] = MyCustomTool()
```

```python
# 3. Importe em app/agents/tools/__init__.py ou base.py
from app.agents.tools.my_tool import MyCustomTool, TOOL_REGISTRY
```

---

## 📌 Notas Finais

Este manual cobre toda a estrutura, padrões e pontos de extensão do projeto. Para qualquer nova funcionalidade, siga o padrão existente: **crie uma classe que herda da base abstrata → registre no registry/router → exponha via route se necessário**.