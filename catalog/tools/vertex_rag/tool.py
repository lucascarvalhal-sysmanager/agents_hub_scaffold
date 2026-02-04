from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag


def build_vertex_rag_tool(params: dict) -> VertexAiRagRetrieval:
    """
    Constrói uma ferramenta de RAG do Vertex AI.

    Args:
        params: Dicionário com configurações:
            - name: Nome da ferramenta (opcional)
            - description: Descrição da ferramenta (obrigatório)
            - rag_corpus: ID do corpus RAG (obrigatório)
            - similarity_top_k: Número de resultados (opcional, default: 10)
            - vector_distance_threshold: Threshold de distância (opcional, default: 0.5)

    Returns:
        VertexAiRagRetrieval configurado
    """
    return VertexAiRagRetrieval(
        name=params.get("name", "retrieve_rag_documentation"),
        description=params["description"],
        rag_resources=[
            rag.RagResource(
                rag_corpus=params["rag_corpus"]
            )
        ],
        similarity_top_k=params.get("similarity_top_k", 10),
        vector_distance_threshold=params.get("vector_distance_threshold", 0.5),
    )
