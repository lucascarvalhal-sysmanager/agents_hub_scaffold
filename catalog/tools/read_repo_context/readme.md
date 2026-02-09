# Read Repo Context Tool

Lê o contexto completo de um repositório Git e retorna em formato Markdown. Usa o [repomix](https://github.com/yamadashy/repomix) para extrair a estrutura e o conteúdo de todos os arquivos do repositório, permitindo que o agente entenda uma codebase inteira.

## Visão Geral

| | |
|---|---|
| **Kind** | `async_function_tool` |
| **Entry Point** | `tool.read_repo_context` |
| **Requer Autenticação** | Sim (username + token) |
| **Dependências Python** | Nenhuma (biblioteca padrão) |
| **Dependências do Sistema** | `git`, `npx`, `repomix` |

## Como Funciona

A tool é uma função assíncrona que executa dois subprocessos em sequência:

1. **`git clone`** — clona o repositório em um diretório temporário usando as credenciais configuradas
2. **`npx repomix --stdout`** — extrai o contexto completo do repositório em formato Markdown

```
repo_url + branch → git clone (tmpdir) → npx repomix --stdout → Markdown do repositório
```

O diretório temporário é automaticamente removido após a execução.

## Pré-requisitos

Estas ferramentas precisam estar instaladas no sistema onde o agente roda:

```bash
# Git
git --version

# Node.js e npx
node --version
npx --version

# repomix (instalado automaticamente via npx na primeira execução)
npx -y repomix --version
```

## Configuração

Defina as credenciais do repositório via variáveis de ambiente no `.env`:

```bash
GITHUB_USERNAME=seu_usuario
GITHUB_TOKEN=ghp_seu_token_aqui
```

As variáveis são referenciadas no `config.yaml` com a sintaxe `${VAR}`.

## Uso

### Importando a função

```python
from catalog.tools.read_repo_context import read_repo_context
```

### Chamando a função (async)

```python
context = await read_repo_context(
    repo_url="https://github.com/usuario/repo",
    branch="main",
)
```

### Assinatura

```python
async def read_repo_context(repo_url: str, branch: str) -> str
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `repo_url` | `str` | URL do repositório Git |
| `branch` | `str` | Branch a ser clonada |

**Retorno:** string com o conteúdo completo do repositório em Markdown.

> As credenciais (provider, username, token) são lidas automaticamente do `container.py` via `services.setup_code_repo_auth`. Não precisam ser passadas como parâmetro.

### Tratamento de Erros

A versão pre_built (usada pelo agente) retorna strings de erro em vez de exceções:

```python
"Erro: configurações de autenticação incompletas (username, token ou provider)."
"Erro: URL 'url' não pertence ao provedor 'provider'."
"Erro: falha ao clonar 'url'. Verifique se a URL e a branch estão corretas."
"Erro: falha ao executar repomix no repositório."
```

## Registro no Agente

### 1. Enum

O kind está registrado em `agents/core/domain/agent/enums.py`:

```python
class PreBuiltTools(str, Enum):
    READ_REPO_CONTEXT = "read_repo_context"
```

### 2. Wrapper pre_built

A versão pre_built em `agents/utils/pre_built_functions.py` lê as credenciais do container automaticamente, permitindo que o agente chame a tool passando apenas `repo_url` e `branch`.

### 3. Mapeamento no Builder

Registrado em `agents/core/adapters/agent_builder/adk_tools_builder.py`:

```python
PreBuiltTools.READ_REPO_CONTEXT: lambda _: pre_built_functions.read_repo_context,
```

### 4. Configuração no YAML

Em `config/agent/config.yaml`:

```yaml
agent:
  tools:
    - read_repo

tools:
  - name: read_repo
    transport: pre_built
    kind: read_repo_context
    provider: github
    connection_config:
      username: ${GITHUB_USERNAME}
      token: ${GITHUB_TOKEN}
```

## Estrutura

```
read_repo_context/
├── __init__.py        # Exporta read_repo_context
├── tool.py            # Implementação async com git clone + repomix
├── spec.yaml          # Metadados e configuração
├── requirements.txt   # Sem dependências Python (requer git e npx no sistema)
└── readme.md          # Esta documentação
```
