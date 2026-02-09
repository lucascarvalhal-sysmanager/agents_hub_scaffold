# FinOps After Model Callback

Callback que coleta métricas de uso após a chamada ao modelo.

## Funcionalidade

- Extrai métricas de uso do LLM response
- Cria relatórios FinOps
- Processa side-channels (traduções, etc)
- Armazena em buffer para persistência em batch

## Uso

```yaml
# config.yaml
agent:
  name: meu_agente
  callbacks:
    after_model_callback:
      - collect_finops_metrics
```

```python
from catalog.callbacks.finops_after_model import collect_finops_metrics

agent = LlmAgent(
    name="meu_agente",
    after_model_callback=collect_finops_metrics
)
```

## Métricas Coletadas

| Métrica | Descrição |
|---------|-----------|
| prompt_token_count | Tokens do prompt |
| candidates_token_count | Tokens da resposta |
| thoughts_token_count | Tokens de pensamento |
| total_token_count | Total de tokens |
| cached_content_token_count | Tokens em cache |
| execution_time_ms | Tempo de execução |

## Dependências

- google-adk
- finops_persistence (do catálogo)
- finops_before_model (do catálogo)
