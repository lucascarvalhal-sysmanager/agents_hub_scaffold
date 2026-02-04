# Read Repo Context Tool

Lê o contexto completo de um repositório Git usando repomix.

## Funcionalidade

- Clona repositórios públicos ou privados
- Executa `npx repomix --stdout` para extrair contexto
- Suporta autenticação via username/token
- Função assíncrona com tratamento de erros robusto

## Pré-requisitos

- Git instalado no sistema
- Node.js e npx instalados
- repomix (instalado automaticamente via npx)

## Uso

```python
from catalog.tools.read_repo_context import read_repo_context

context = await read_repo_context(
    repo_url="https://github.com/usuario/repo",
    branch="main",
    provider="github",
    username="meu_usuario",
    token="meu_token"
)
```

## Parâmetros

| Parâmetro | Descrição | Obrigatório |
|-----------|-----------|-------------|
| repo_url | URL do repositório | Sim |
| branch | Branch a ser clonada | Sim |
| provider | Provedor (github, gitlab) | Sim |
| username | Usuário para autenticação | Sim |
| token | Token para autenticação | Sim |

## Erros

- `RepoReadError`: Erro genérico ao ler repositório

## Dependências do Sistema

- git
- npx (Node.js)
