# Google Search Tool

Agente especializado em realizar buscas no Google.

## Funcionalidade

- Usa o modelo Gemini 2.5 Flash
- Integrado com a ferramenta nativa `google_search` do ADK
- Retorna resultados de busca formatados

## Uso

```python
from catalog.tools.google_search import search_agent_tool

agent = LlmAgent(
    name="meu_agente",
    tools=[search_agent_tool]
)
```

## Dependências

- google-adk
