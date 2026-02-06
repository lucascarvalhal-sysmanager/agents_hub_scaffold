# Datetime Tool

Ferramenta para obter data e hora atual em diferentes idiomas.

## Funcionalidade

Uma única função `get_current_datetime()` que:
- Retorna data/hora formatada
- Suporta português (PT-BR) e inglês (EN-US)
- Permite incluir ou omitir o horário

## Uso

```python
from catalog.tools.datetime_tool import get_current_datetime

# Com horário (padrão)
print(get_current_datetime())
# PT: "Quinta-feira, 6 de Fevereiro de 2026, 14:30:45"
# EN: "Thursday, February 6, 2026, 14:30:45"

# Apenas data
print(get_current_datetime(include_time=False))
# PT: "Quinta-feira, 6 de Fevereiro de 2026"
# EN: "Thursday, February 6, 2026"
```

## Função

### get_current_datetime(include_time: bool = True) -> str

Retorna data/hora atual formatada.

**Parâmetros:**
- `include_time`: Se `True` (padrão), inclui horário. Se `False`, retorna só a data.

**Retorno:**
- String formatada com data e opcionalmente hora.

**Idioma:**
- Definido pela variável de ambiente `DATETIME_LANGUAGE`
- Valores: `pt` (padrão) ou `en`

## Configuração

```bash
# No .env
DATETIME_LANGUAGE=pt  # ou "en" para inglês
```

## Dependências

Nenhuma - usa apenas a biblioteca padrão do Python.
