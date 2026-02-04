# Vertex RAG Tool

Ferramenta de RAG (Retrieval Augmented Generation) usando Vertex AI.

## Funcionalidade

- Recupera documentos relevantes de um corpus RAG
- Configurável via parâmetros
- Integrado com Vertex AI

## Uso

```python
from catalog.tools.vertex_rag import build_vertex_rag_tool

rag_tool = build_vertex_rag_tool({
    "name": "meu_rag",
    "description": "Busca documentação interna",
    "rag_corpus": "projects/meu-projeto/locations/us-central1/ragCorpora/123",
    "similarity_top_k": 5,
    "vector_distance_threshold": 0.7
})

agent = LlmAgent(
    name="meu_agente",
    tools=[rag_tool]
)
```

## Parâmetros

| Parâmetro | Descrição | Obrigatório | Default |
|-----------|-----------|-------------|---------|
| name | Nome da ferramenta | Não | retrieve_rag_documentation |
| description | Descrição da ferramenta | Sim | - |
| rag_corpus | ID do corpus RAG | Sim | - |
| similarity_top_k | Número de resultados | Não | 10 |
| vector_distance_threshold | Threshold de distância | Não | 0.5 |

## Dependências

- google-adk
- google-cloud-aiplatform
