# FinOps Before Model Callback

Callback que captura métricas iniciais antes da chamada ao modelo.

## Funcionalidade

- Captura timestamp de início para cálculo de latência
- Faz snapshot do estado de uso atual
- Captura metadados da requisição (modelo, prompt)

## Uso

```yaml
# config.yaml
agent:
  name: meu_agente
  callbacks:
    before_model_callback:
      - finops_before_model_callback
```

```python
from catalog.callbacks.finops_before_model import finops_before_model_callback

agent = LlmAgent(
    name="meu_agente",
    before_model_callback=finops_before_model_callback
)
```

## Dados Capturados

| State Key | Descrição |
|-----------|-----------|
| temp:finops_start_time | Timestamp de início |
| temp:finops_pre_usage | Snapshot de uso anterior |
| temp:finops_model_name | Nome do modelo |
| temp:finops_user_prompt | Prompt do usuário |

## Dependências

- google-adk
- finops_persistence (do catálogo)
