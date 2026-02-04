# Tools

Ferramentas individuais disponíveis para uso em agentes.

## Tools Disponíveis

| Tool | Descrição | Categoria |
|------|-----------|-----------|
| [google_search](./google_search/) | Agente especializado em buscas Google | search |
| [smart_search_tool](./smart_search_tool/) | Pesquisa inteligente com resultados estruturados | search |
| [vertex_rag](./vertex_rag/) | RAG usando Vertex AI | retrieval |
| [read_repo_context](./read_repo_context/) | Lê contexto de repositórios Git | repository |
| [send_email](./send_email/) | Envio de emails | communication |
| [datetime_tool](./datetime_tool/) | Data e hora atual | utility |

## Estrutura de cada Tool

```
tool_name/
├── __init__.py      # Exports
├── tool.py          # Código principal
├── spec.yaml        # Metadados e configuração
├── requirements.txt # Dependências Python
└── readme.md        # Documentação
```

## Como adicionar uma nova Tool

1. Crie uma pasta com o nome da tool
2. Adicione os arquivos obrigatórios
3. Preencha o `spec.yaml` com os metadados
4. Documente no `readme.md`
5. Atualize este README
