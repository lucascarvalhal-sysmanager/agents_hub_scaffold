# Callbacks

Callbacks reutilizáveis para agentes.

## Callbacks Disponíveis

| Callback | Tipo | Descrição |
|----------|------|-----------|
| [translate_thought](./translate_thought/) | after_model_callback | Traduz pensamentos para português |
| [finops_persistence](./finops_persistence/) | service | Serviço de persistência para FinOps |
| [finops_before_model](./finops_before_model/) | before_model_callback | Captura métricas antes da chamada |
| [finops_after_model](./finops_after_model/) | after_model_callback | Coleta métricas após a chamada |
| [finops_after_agent](./finops_after_agent/) | after_agent_callback | Persiste relatórios em batch |

## Fluxo FinOps

```
1. finops_before_model  →  Captura timestamp e estado inicial
         ↓
2. [Execução do modelo]
         ↓
3. translate_thought    →  Traduz pensamentos (opcional)
3. finops_after_model   →  Coleta métricas e bufferiza
         ↓
4. [Resposta do agente]
         ↓
5. finops_after_agent   →  Persiste no BigQuery
```

## Estrutura de cada Callback

```
callback_name/
├── __init__.py      # Exports
├── callback.py      # Código principal (ou hooks.py)
├── spec.yaml        # Metadados e configuração
├── requirements.txt # Dependências Python
└── readme.md        # Documentação
```

## Como adicionar um novo Callback

1. Crie uma pasta com o nome do callback
2. Adicione os arquivos obrigatórios
3. Preencha o `spec.yaml` com os metadados
4. Documente no `readme.md`
5. Atualize este README
