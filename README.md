# API IA — Central Corporativa de Inteligência Artificial

Central interna de inteligência artificial construída com **FastAPI** em Python. Projetada para ser leve, simples e fácil de evoluir no ambiente corporativo com internet bloqueada.

## 📋 Índice

- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Execução](#execução)
- [Endpoints](#endpoints)
- [Configuração](#configuração)
- [Segurança](#segurança)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Desenvolvimento](#desenvolvimento)

---

## Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Clients   │────▶│  FastAPI Core│────▶│  Providers   │
│ (apps internos) │    │  (API IA)    │     │  Local/Online  │
└─────────────┘     └──────────────┘     │  Corporate     │
                                        └──────┬───────┘
                                               │
                                        ┌──────▼───────┐
                                        │   Agents     │
                                        │   Tools      │
                                        │   SQL Read-Only│
                                        └──────────────┘
```

### Componentes

| Camada | Descrição |
|--------|-----------|
| **Providers** | Abstração sobre múltiplos backends de IA (local mock, online, corporativo) via `ProviderRouter` |
| **Agents** | Executores simples com loop controlado (`AgentRunner`) — ex: `ResearchAgent` |
| **Tools** | Ferramentas internas acessíveis por agents (ex: `SQLReadOnlyTool`) |
| **SQL** | Validador que bloqueia tudo exceto SELECT + registry de queries aprovadas |
| **Services** | Orquestradores de alto nível (chat, agent, audit, session) |
| **Repositories** | Camada de persistência (estrutura pronta para futuro com banco) |
| **Schemas** | Modelos Pydantic para requests/responses padronizados |

---

## Instalação

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Instalar dependências (offline)
pip install --no-index --find-links=./packages -r requirements.txt

# Ou se houver internet disponível:
pip install -r requirements.txt
```

---

## Execução

```bash
# Iniciar servidor de desenvolvimento
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Ou para produção (sem reload):
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Alternativa via Python:
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)"
```

A API estará disponível em `http://localhost:8000` com documentação interativa em `/docs`.

---

## Endpoints

### Básicos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações básicas da API |
| GET | `/info` | Informações detalhadas + configuração |
| GET | `/health` | Health check básico |
| GET | `/v1/health` | Health check v1 (mesma resposta) |

### Providers

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/v1/providers` | Lista providers de IA |
| GET | `/v1/providers/{id}` | Info detalhada do provider |
| POST | `/v1/providers/{id}/test` | Testa conexão com provider |

### Chat Completions

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/v1/chat/completions` | Chat completions via provider |
| GET | `/v1/chat/models` | Modelos disponíveis |

### Agents

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/v1/agents` | Lista agentes |
| POST | `/v1/agents/{agent_id}/run` | Executa um agente |
| GET | `/v1/agents/{agent_id}` | Info do agente |

### Tools

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/v1/tools` | Lista ferramentas |
| POST | `/v1/tools/{name}/execute` | Executa uma ferramenta |

---

## Exemplos de Uso

### Chat completions

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Olá, como você está?"}
    ],
    "provider": "local"
  }'
```

### Research Agent

```bash
curl -X POST http://localhost:8000/v1/agents/research/run \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Quais são as tabelas disponíveis?",
    "params": {"tool": "sql_readonly", "query": "SELECT TOP 1 * FROM INFORMATION_SCHEMA.TABLES"}
  }'
```

---

## Configuração

Copie `.env.example` para `.env` e ajuste as variáveis:

```bash
cp .env.example .env
```

### Variáveis disponíveis

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `APP_NAME` | `API IA` | Nome da aplicação |
| `VERSION` | `0.1.0` | Versão da API |
| `HOST` | `0.0.0.0` | Host do servidor |
| `PORT` | `8000` | Porta do servidor |
| `DEBUG` | `true` | Modo debug (reload) |
| `LOG_LEVEL` | `INFO` | Nível de log (DEBUG, INFO, WARNING, ERROR) |

### Providers

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `PROVIDER_LOCAL_ENABLED` | `true` | Habilita provider local |
| `PROVIDER_ONLINE_ENABLED` | `false` | Habilita provider online |
| `PROVIDER_CORPORATE_ENABLED` | `false` | Habilita provider corporativo |

---

## Segurança

- **SQL**: Apenas SELECT é permitido. INSERT, UPDATE, DELETE, DROP e outros comandos são bloqueados pelo validador.
- **Providers**: Mockados por padrão — sem conexão externa.
- **Sem secrets**: Nenhuma credencial real no código-fonte.
- **CORS**: Permite todas as origens (configure para produção).

---

## Estrutura do Projeto

```
api-ia/
├── app/
│   ├── main.py              # Entry point FastAPI (use este)
│   ├── config.py            # Configurações via variáveis de ambiente (.env)
│   ├── dependencies.py      # Dependências injetadas (FastAPI Depends)
│   ├── api/v1/              # Rotas HTTP (health, providers, chat, agents, tools)
│   ├── core/                # Logging, security, permissions, exceptions
│   ├── providers/           # BaseProvider + Local/Online/Corporate + Router
│   ├── agents/              # BaseAgent, AgentRunner, ResearchAgent, Tools
│   ├── sql/                 # Validators, Registry (queries aprovadas)
│   ├── services/            # Chat, Agent, Audit, Session services
│   ├── repositories/        # Audit, Message, Request repositories
│   └── schemas/             # Pydantic models
├── tests/                   # Testes (pytest)
├── scripts/                 # Scripts utilitários (future)
├── requirements.txt         # Dependências
├── .env.example            # Variáveis de ambiente
├── .gitignore              # Ignorar arquivos
└── README.md               # Este arquivo
```

---

## Desenvolvimento

### Inicialização rápida

1. Clone o repositório: `git clone <repo-url>`
2. Crie e ative o venv (ver [Instalação](#instalação))
3. Copie `.env.example` para `.env`
4. Execute a API (ver [Execução](#execução))
5. Acesse `http://localhost:8000/docs` para testar interativamente

### Testes

```bash
pytest tests/ -v
```

---

## Evolução Futura

- [ ] Conectar SQL provider ao SQL Server real (pyodbc)
- [ ] Persistência de auditoria em banco
- [ ] Autenticação com JWT/API keys reais
- [ ] Rate limiting e throttling
- [ ] Testes automatizados (pytest)
- [ ] Container Docker