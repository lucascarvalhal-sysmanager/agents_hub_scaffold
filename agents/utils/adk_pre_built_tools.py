"""
ADK Pre-Built Tools - Ferramentas pré-construídas para agentes.
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

# SearchAgent
search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    instruction="""You're a specialist in Google Search""",
    tools=[google_search],
)
search_agent_tool = AgentTool(search_agent)


def build_vertex_rag_tool(params: dict):
    """
    Constrói ferramenta de RAG com Vertex AI.
    Import lazy para evitar erro quando llama_index não está instalado.
    """
    try:
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
        from vertexai.preview import rag

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
    except ImportError as e:
        raise ImportError(
            f"Para usar vertex_rag, instale: pip install llama-index. Erro: {e}"
        )
