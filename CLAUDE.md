# CLAUDE.md - Contexto do Projeto

Este arquivo mantém o contexto para sessões futuras do Claude Code.

## Visão Geral

**Projeto:** Agents Hub Scaffold
**Objetivo:** Framework para construção de agentes de IA usando Google ADK (Agent Development Kit)
**Organização:** Eneva Foundations IA

## Arquitetura

```
Scaffold/
├── agents/                    # Código do agente
│   ├── agent.py              # Entry point do agente
│   ├── container.py          # Injeção de dependências
│   ├── core/                 # Núcleo do framework
│   │   ├── adapters/         # Adaptadores (builders)
│   │   └── domain/           # Domínio (enums, exceptions)
│   ├── helpers/              # Re-exports dos callbacks
│   └── utils/                # Re-exports das tools
│
├── catalog/                   # CATÁLOGO DE GOVERNANÇA
│   ├── tools/                # Ferramentas individuais
│   ├── skills/               # Fluxos que combinam tools
│   └── callbacks/            # Hooks do ciclo de vida
│
├── config/
│   ├── agent/config.yaml     # Configuração do agente
│   └── schema/               # Validação de schema
│
├── main.py                   # Entry point da API
└── .env                      # Variáveis de ambiente
```

## Catálogo

### Tools (catalog/tools/)

| Tool | Tipo | Descrição |
|------|------|-----------|
| `google_search` | AgentTool | Busca no Google (SearchAgent) |
| `smart_search_tool` | AgentTool | Busca estruturada (SmartSearchAgent) |
| `vertex_rag` | FunctionTool | RAG com Vertex AI |
| `read_repo_context` | FunctionTool | Lê repositórios GitHub |
| `send_email` | FunctionTool | Envia emails |
| `datetime_tool` | FunctionTool | Data/hora atual (PT, EN, ES) via TRANSLATIONS |

### Skills (catalog/skills/)

| Skill | Descrição | Tools usadas |
|-------|-----------|--------------|
| `analyze_performance` | Relatório de métricas e custos | Nenhuma (processa dados) |
| `smart_search` | Processa resultados de busca | google_search |

### Callbacks (catalog/callbacks/)

| Callback | Tipo | Descrição |
|----------|------|-----------|
| `translate_thought` | after_model | Traduz pensamentos para PT-BR |
| `finops_before_model` | before_model | Captura timestamp início |
| `finops_after_model` | after_model | Coleta métricas de uso |
| `finops_after_agent` | after_agent | Persiste e gera relatório |
| `finops_persistence` | service | Serviço de persistência BigQuery |

## Configuração Atual

### Modelos
- **Agente principal:** `gemini-2.5-pro`
- **Tradução:** `gemini-2.5-flash-lite`
- **Sub-agentes (search):** `gemini-2.5-flash`

### Variáveis de Ambiente (.env)
```env
GOOGLE_CLOUD_PROJECT=eva-prj-dev-ai-foundations-fi
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
LOCAL_DEVELOPMENT=true
LOG_LEVEL=INFO

# Performance Report
PERFORMANCE_REPORT_ENABLED=true
PERFORMANCE_REPORT_LOG=true
PERFORMANCE_REPORT_SAVE=true
PERFORMANCE_REPORT_DIR=.adk/performance_reports
```

## Fluxo de Execução

```
Usuário envia mensagem
    │
    ▼
[finops_before_model] → Captura timestamp
    │
    ▼
[Modelo processa] → gemini-2.5-pro
    │
    ▼
[translate_thought] → Traduz pensamento (gemini-2.5-flash-lite)
[finops_after_model] → Coleta métricas
    │
    ▼
[Tool chamada] → Ex: SmartSearchAgent
    │
    ▼
[Agente responde]
    │
    ▼
[finops_after_agent] → Persiste métricas
                     → Gera relatório de performance
                     → Salva em .adk/performance_reports/
```

## Estrutura de cada componente do Catálogo

```
component_name/
├── __init__.py           # Exports
├── tool.py / skill.py / callback.py / hooks.py
├── spec.yaml             # Metadados e configuração
├── requirements.txt      # Dependências
└── readme.md             # Documentação
```

## Comandos Úteis

```bash
# Iniciar aplicação
source .venv/bin/activate
python main.py

# Ver logs
tail -f /tmp/scaffold.log

# Ver relatórios de performance
cat .adk/performance_reports/*.md
```

## Conceitos Importantes

### Tool vs Skill vs Callback

| Componente | Quando usar | Quem chama |
|------------|-------------|------------|
| **Tool** | Ação simples e isolada | Agente chama |
| **Skill** | Fluxo complexo com múltiplas etapas | Tool ou Callback chama |
| **Callback** | Automático em eventos do ciclo de vida | Framework chama |

### Hierarquia
```
Callbacks → Skills → Tools
    │          │        │
    │          │        └── Ações atômicas
    │          └── Orquestração de fluxos
    └── Eventos automáticos
```

## Registro de Tools (PreBuiltTools)

Para adicionar uma nova tool pre_built:

1. Adicionar enum em `agents/core/domain/agent/enums.py`:
```python
class PreBuiltTools(str, Enum):
    MINHA_TOOL = "minha_tool"
```

2. Registrar em `agents/core/adapters/agent_builder/adk_tools_builder.py`:
```python
pre_built_functions_map = {
    PreBuiltTools.MINHA_TOOL: lambda _: minha_tool,
}
```

3. Exportar em `agents/utils/adk_pre_built_tools.py`

4. Configurar no `config.yaml` usando `kind` (não `type`):
```yaml
tools:
  - name: minha_tool
    transport: pre_built
    kind: minha_tool      # ← usar 'kind', não 'type'
```

## Filosofia de Código

- **Dados separados de lógica** - constantes no topo, comportamento embaixo
- **Uma função faz o trabalho** - só quebra em mais quando realmente precisa
- **Sem repetição** - se algo se repete, vira dado, não código duplicado
- **Erros como retorno** - tools retornam strings de erro (não exceções), para o ADK não quebrar
- **Prático e direto** - faz o que precisa, sem over-engineering

Exemplo (datetime_tool):
```python
TRANSLATIONS = {
    "pt": { "days": [...], "months": [...], "format": "..." },
    "en": { "days": [...], "months": [...], "format": "..." },
}

def get_current_datetime():
    language = os.getenv("DATETIME_LANGUAGE", "pt")
    trans = TRANSLATIONS.get(language, TRANSLATIONS["pt"])
```

**Para adicionar novo idioma:** apenas adicionar entrada no TRANSLATIONS, sem criar nova função.

## Diferença: type vs kind

| Campo | Localização | Função |
|-------|-------------|--------|
| `type` | Raiz do YAML | Tipo de fluxo do agente (`single`, `hierarchical`, `sequential`) |
| `kind` | Dentro de tool pre_built | Qual ferramenta pré-construída usar |

```yaml
type: single              # ← Fluxo do agente
tools:
  - name: get_datetime
    transport: pre_built
    kind: get_current_datetime  # ← Tipo da ferramenta
```

## Próximos Passos Sugeridos

1. Implementar mais skills (ex: `review_pr`, `daily_report`)
2. Adicionar persistência histórica para comparação de performance
3. Criar dashboard de métricas
4. Implementar cache para buscas repetidas

## Histórico de Desenvolvimento

- **2026-02-06:** Refatoração read_repo_context e correção container.py
  - Corrigido container.py para buscar tools por `kind` em vez de `type`
  - Refatorado read_repo_context: subprocess unificado com `communicate()`, erros como retorno string
  - Removido `RepoReadError` (usa RuntimeError no catálogo, retorno string no pre_built)
  - Corrigida validação: `or` → `and` (exige todos os campos de autenticação)
  - Renomeado `dispatch_map` → `TRANSLATIONS` no datetime_tool
  - Adicionado `--style markdown` no repomix

- **2026-02-06:** Refatoração de configuração e datetime_tool
  - Renomeado campo `type` para `kind` nas tools pre_built (evita conflito com `type: single` do agente)
  - Atualizado schema_validator.yaml para validar `kind`
  - Unificado datetime_tool em uma única função `get_current_datetime(include_time=True)`
  - Implementado padrão dispatch_map baseado em dados (não funções)
  - Adicionado suporte a espanhol (ES) no datetime_tool
  - Removida função `formatted_date_today` (substituída por `get_current_datetime(include_time=False)`)
  - Alterado agente para responder no mesmo idioma da pergunta do usuário

- **2026-02-04:** Implementação inicial do catálogo
  - Criado estrutura catalog/ com tools, skills e callbacks
  - Migrado código de agents/utils e agents/helpers para catálogo
  - Implementado skill `analyze_performance` com relatório automático
  - Implementado `smart_search_tool` com resultados estruturados
  - Integrado callbacks FinOps com skill de performance
  - Refatorado datetime_tool com suporte multi-idioma

## Arquivos Importantes

- `config/agent/config.yaml` - Configuração do agente (usa `kind` para pre_built tools)
- `config/schema/schema_validator.yaml` - Validação de schema do config
- `agents/core/adapters/agent_builder/adk_builder.py` - Construtor do agente
- `agents/core/adapters/agent_builder/adk_tools_builder.py` - Construtor de tools (busca `kind`)
- `agents/utils/prompt_functions.py` - FunctionTools para o agente
- `catalog/tools/datetime_tool/tool.py` - Exemplo de TRANSLATIONS baseado em dados
- `catalog/callbacks/finops_after_agent/callback.py` - Integração skill + callback
- `catalog/skills/analyze_performance/skill.py` - Lógica de análise de performance
