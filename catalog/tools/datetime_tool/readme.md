# Datetime Tool

Ferramentas para obter data e hora atual em diferentes formatos.

## Funcionalidade

- `get_current_datetime()`: Data/hora em português do Brasil
- `formatted_date_today()`: Data em inglês

## Uso

```python
from catalog.tools.datetime_tool import get_current_datetime, formatted_date_today

# Português
print(get_current_datetime())
# Saída: "Segunda-feira, 4 de Fevereiro de 2026, 14:30:00"

# Inglês
print(formatted_date_today())
# Saída: "Today is monday, february 4, 2026."
```

## Funções

### get_current_datetime()

Retorna data e hora em português do Brasil.

**Formato:** `{Dia da semana}, {dia} de {Mês} de {ano}, {HH:MM:SS}`

### formatted_date_today()

Retorna apenas a data em inglês.

**Formato:** `Today is {weekday}, {month} {day}, {year}.`

## Dependências

Nenhuma - usa apenas a biblioteca padrão do Python.
