# Google Search Tool

Agente especializado em buscas no Google. Diferente de uma `function_tool`, esta é uma `agent_tool`, um sub-agente com modelo próprio que recebe a query, executa a busca e retorna os resultados processados.

## Visão Geral

| | |
|---|---|
| **Kind** | `agent_tool` |
| **Modelo** | `Coloque seu modelo de preferência (ex: gemini-2.5-flash)` |
| **Entry Point** | `tool.search_agent_tool` |
| **Dependências** | `google-adk>=1.9.0` |

## Como Funciona

A tool cria um sub-agente ADK com acesso à ferramenta nativa `google_search` do Google ADK. Quando o agente principal precisa buscar informações, ele delega para este sub-agente, que:

1. Recebe a query do agente principal
2. Executa a busca via `google_search` (ferramenta nativa do ADK)
3. Processa os resultados com o modelo da sua preferência
4. Retorna a resposta formatada ao agente principal

```
Agente Principal → SearchAgent (gemini-2.5-flash) → google_search API → Resultados
```

## Uso

### Importando a tool

```python
from catalog.tools.google_search import search_agent_tool
```

### Usando diretamente com um agente ADK

```python
from google.adk.agents import Agent

agent = Agent(
    name="meu_agente",
    model="",
    tools=[search_agent_tool],
)
```

## Registro no Agente

### 1. Enum

O kind está registrado em `agents/core/domain/agent/enums.py`:

```python
class PreBuiltTools(str, Enum):
    GOOGLE_SEARCH = "SearchAgent"
```

### 2. Sub-agente como AgentTool

O sub-agente é criado em `agents/utils/adk_pre_built_tools.py` e encapsulado como `AgentTool`:

```python
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    instruction="""You're a specialist in Google Search""",
    tools=[google_search],
)

search_agent_tool = AgentTool(search_agent)
```

### 3. Mapeamento no Builder

Registrado em `agents/core/adapters/agent_builder/adk_tools_builder.py`:

```python
PreBuiltTools.GOOGLE_SEARCH: lambda _: adk_pre_built_tools.search_agent_tool,
```

### 4. Configuração no YAML

Em `config/agent/config.yaml`:

```yaml
agent:
  tools:
    - SearchAgent

tools:
  - name: SearchAgent
    transport: pre_built
    kind: SearchAgent
```

## Estrutura

```
google_search/
├── __init__.py        # Exporta search_agent_tool
├── tool.py            # Cria o sub-agente e o AgentTool
├── spec.yaml          # Metadados e configuração
├── requirements.txt   # google-adk>=1.9.0
└── readme.md          # Esta documentação
```
