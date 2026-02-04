# FinOps Persistence

Serviço de persistência para relatórios FinOps com suporte a BigQuery.

## Funcionalidade

- `FinopsReport`: DTO para relatórios de uso
- `BigQueryProvider`: Persistência no BigQuery
- `PersistenceFactory`: Factory para criar serviços

## Uso

```python
from catalog.callbacks.finops_persistence import (
    FinopsReport,
    PersistenceFactory
)

# Criar serviço via factory (usa variáveis de ambiente)
service = PersistenceFactory.create_service()

# Criar relatório
report = FinopsReport(
    user_id="user123",
    model_name="gemini-2.5-flash",
    total_token_count=1500,
    interaction_kind="agent"
)

# Persistir
if service:
    service.save_report(report)
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| FINOPS_PROVIDER_TYPE | Tipo do provider (bigquery) |
| FINOPS_BQ_PROJECT_ID | ID do projeto GCP |
| FINOPS_BQ_DATASET_ID | ID do dataset |
| FINOPS_BQ_TABLE_ID | ID da tabela |

## Dependências

- google-cloud-bigquery
