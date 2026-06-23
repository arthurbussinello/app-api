# API IA — Hub Corporativo de Inteligência Artificial

Hub interno de inteligência artificial construído com **FastAPI** em Python. Projetado para ser leve, simples e fácil de evoluir no ambiente corporativo com internet bloqueada.

## Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Clients   │────▶│  FastAPI Hub │────▶│  Providers   │
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

## Execução

```bash
# Iniciar servidor de desenvolvimento
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Ou usando o entry point direto:
python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

A API estará disponível em `http://localhost:8000` com documentação interativa em `/docs`.

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check básico |
| GET | `/v1/health` | Health check v1 |
| GET | `/v1/providers` | Lista providers de IA |
| GET | `/v1/providers/{id}` | Info detalhada do provider |
| POST | `/v1/chat/completions` | Chat completions via provider |
| GET | `/v1/chat/models` | Modelos disponíveis |
| POST | `/v1/agents/{agent_id}/run` | Executa um agente |
| GET | `/v1/agents` | Lista agentes |
| GET | `/v1/agents/{agent_id}` | Info do agente |
| POST | `/v1/tools/{name}/execute` | Executa uma ferramenta |
| GET | `/v1/tools` | Lista ferramentas |

## Exemplo de uso — Chat completions

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

## Exemplo de uso — Research Agent

```bash
curl -X POST http://localhost:8000/v1/agents/research/run \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Quais são as tabelas disponíveis?",
    "params": {"tool": "sql_readonly", "query": "SELECT TOP 1 * FROM INFORMATION_SCHEMA.TABLES"}
  }'
```

## Configuração

Copie `.env.example` para `.env` e ajuste as variáveis:

```bash
cp .env.example .env
```

Variáveis disponíveis:
- `APP_NAME` — Nome da aplicação
- `VERSION` — Versão da API
- `HOST` — Host do servidor (default: 0.0.0.0)
- `PORT` — Porta do servidor (default: 8000)
- `LOG_LEVEL` — Nível de log (DEBUG, INFO, WARNING, ERROR)

## Segurança

- **SQL**: Apenas SELECT é permitido. INSERT, UPDATE, DELETE, DROP e outros comandos são bloqueados pelo validador.
- **Providers**: Mockados por padrão — sem conexão externa.
- **Sem secrets**: Nenhuma credencial real no código-fonte.

## Estrutura do Projeto

```
api-ia/
├── app/
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Configurações via variáveis de ambiente
│   ├── dependencies.py      # Dependências injetadas
│   ├── api/v1/              # Rotas HTTP (health, providers, chat, agents, tools)
│   ├── core/                # Logging, security, permissions, exceptions
│   ├── providers/           # BaseProvider + Local/Online/Corporate + Router
│   ├── agents/              # BaseAgent, AgentRunner, ResearchAgent, Tools
│   ├── sql/                 # Validators, Registry (queries aprovadas)
│   ├── services/            # Chat, Agent, Audit, Session services
│   ├── repositories/        # Audit, Message, Request repositories
│   └── schemas/             # Pydantic models
├── tests/                   # Testes futuros
├── scripts/                 # Scripts utilitários
├── requirements.txt         # Dependências
├── .env.example            # Variáveis de ambiente
├── .gitignore              # Ignorar arquivos
└── README.md               # Este arquivo
```

## Evolução Futura

- [ ] Conectar SQL provider ao SQL Server real (pyodbc)
- [ ] Persistência de auditoria em banco
- [ ] Autenticação com JWT/API keys reais
- [ ] Rate limiting e throttling
- [ ] Testes automatizados (pytest)
- [ ] Container Docker