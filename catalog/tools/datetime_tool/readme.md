# Datetime Tool

Ferramenta para obter data e hora atual formatada, com suporte a múltiplos idiomas. O agente utiliza esta tool quando precisa informar a data ou horário atual ao usuário.

## Visão Geral

| | |
|---|---|
| **Kind** | `function_tool` |
| **Entry Point** | `tool.get_current_datetime` |
| **Dependências** | Nenhuma (biblioteca padrão) |

## Idiomas Suportados

| Código | Idioma | Exemplo de saída |
|:------:|--------|------------------|
| `pt` | Português (padrão) | Quinta-feira, 6 de Fevereiro de 2026, 14:30:45 |
| `en` | Inglês | Thursday, February 6, 2026, 14:30:45 |
| `es` | Espanhol | Jueves, 6 de Febrero de 2026, 14:30:45 |

## Como Funciona

A tool usa um dicionário `TRANSLATIONS` com os nomes dos dias, meses e formato de cada idioma. Uma única função consulta a variável de ambiente `DATETIME_LANGUAGE`, busca a tradução correspondente e formata a data atual.

```
DATETIME_LANGUAGE=pt → TRANSLATIONS["pt"] → "Quinta-feira, 6 de Fevereiro de 2026, 14:30:45"
```

## Configuração

Defina o idioma via variável de ambiente no `.env`:

```bash
DATETIME_LANGUAGE=pt    # Português (padrão)
DATETIME_LANGUAGE=en    # Inglês
DATETIME_LANGUAGE=es    # Espanhol
```

Se a variável não estiver definida, o idioma padrão é `pt`.

## Uso

### Importando a função

```python
from catalog.tools.datetime_tool import get_current_datetime
```

### Obtendo data e hora

```python
get_current_datetime()
# "Quinta-feira, 6 de Fevereiro de 2026, 14:30:45"
```

### Obtendo apenas a data

```python
get_current_datetime(include_time=False)
# "Quinta-feira, 6 de Fevereiro de 2026"
```

### Assinatura

```python
def get_current_datetime(include_time: bool = True) -> str
```

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|:------:|-----------|
| `include_time` | `bool` | `True` | Se `False`, retorna apenas a data sem horário |

**Retorno:** string formatada com data (e opcionalmente hora) no idioma configurado.

## Registro no Agente

Para que o agente consiga chamar esta tool, ela precisa estar registrada no framework. Abaixo o passo a passo completo.

### 1. Enum

O kind está registrado em `agents/core/domain/agent/enums.py`:

```python
class PreBuiltTools(str, Enum):
    GET_DATETIME = "get_current_datetime"
```

### 2. Wrapper como FunctionTool

A função é encapsulada em um `FunctionTool` do ADK em `agents/utils/prompt_functions.py`. O wrapper adiciona a docstring que o modelo usa para decidir quando chamar a tool:

```python
from catalog.tools.datetime_tool import get_current_datetime as _get_datetime_func

def _get_current_datetime() -> str:
    """
    Retorna a data e hora atual formatada.
    Use esta ferramenta quando precisar saber a data ou hora atual.
    """
    return _get_datetime_func(include_time=True)

get_current_datetime = FunctionTool(_get_current_datetime)
```

### 3. Mapeamento no Builder

Registrado em `agents/core/adapters/agent_builder/adk_tools_builder.py`:

```python
PreBuiltTools.GET_DATETIME: lambda _: prompt_functions.get_current_datetime,
```

### 4. Configuração no YAML

Em `config/agent/config.yaml`:

```yaml
agent:
  tools:
    - get_datetime

tools:
  - name: get_datetime
    transport: pre_built
    kind: get_current_datetime
```

## Como Adicionar um Novo Idioma

Para adicionar suporte a um novo idioma, basta inserir uma entrada no dicionário `TRANSLATIONS` em `tool.py`:

```python
TRANSLATIONS = {
    # idiomas existentes...
    "fr": {
        "days": ["Lundi", "Mardi", "Mercredi", "Jeudi",
                 "Vendredi", "Samedi", "Dimanche"],
        "months": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
        "format": "{day}, {d} {month} {year}, {time}"
    },
}
```

Não é necessário criar novas funções nem alterar nenhum outro arquivo.

## Estrutura

```
datetime_tool/
├── __init__.py        # Exporta get_current_datetime
├── tool.py            # Implementação com TRANSLATIONS
├── spec.yaml          # Metadados e configuração
├── requirements.txt   # Vazio (sem dependências externas)
└── readme.md          # Esta documentação
```
