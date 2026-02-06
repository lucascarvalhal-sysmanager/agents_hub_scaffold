# Translate Thought

Callback que intercepta e traduz os pensamentos (thoughts) do modelo Gemini para português brasileiro.

## Funcionalidade

- Detecta partes da resposta marcadas como `thought=True`
- Traduz automaticamente o texto para português usando Gemini 2.0 Flash
- Contabiliza tokens usados na tradução para FinOps

## Uso

### No config.yaml do agente

```yaml
agent:
  name: meu_agente
  model: gemini-2.5-flash
  callbacks:
    after_model_callback:
      - translate_thought
```

### Import direto

```python
from catalog.tools.translate_thought import translate_thought

# Usar como after_model_callback
agent = LlmAgent(
    name="meu_agente",
    after_model_callback=translate_thought
)
```

## Configuração

| Parâmetro | Descrição | Default |
|-----------|-----------|---------|
| translation_model | Modelo usado para tradução | gemini-2.0-flash |
| min_text_length | Tamanho mínimo para traduzir | 10 |

## Dependências

- google-genai
- google-adk
