# FinOps After Agent Callback

Callback que persiste os relatórios FinOps em batch após a execução do agente.

## Funcionalidade

- Recupera buffer de relatórios do state
- Persiste em batch no BigQuery
- Limpa buffer após persistência

## Uso

```yaml
# config.yaml
agent:
  name: meu_agente
  callbacks:
    after_agent_callback:
      - persist_finops_metrics
```

```python
from catalog.callbacks.finops_after_agent import persist_finops_metrics

agent = LlmAgent(
    name="meu_agente",
    after_agent_callback=persist_finops_metrics
)
```

## Fluxo Completo FinOps

1. `finops_before_model` - Captura início
2. `finops_after_model` - Coleta métricas
3. `finops_after_agent` - Persiste no BigQuery

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| FINOPS_PROVIDER_TYPE | bigquery |
| FINOPS_BQ_PROJECT_ID | ID do projeto |
| FINOPS_BQ_DATASET_ID | ID do dataset |
| FINOPS_BQ_TABLE_ID | ID da tabela |

## Dependências

- google-adk
- google-cloud-bigquery
- finops_persistence (do catálogo)
