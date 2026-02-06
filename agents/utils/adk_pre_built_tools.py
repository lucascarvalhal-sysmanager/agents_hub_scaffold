from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    instruction="""You're a specialist in Google Search""",
    tools=[google_search],
)
search_agent_tool = AgentTool(search_agent)
        
def build_vertex_rag_tool(params: dict) -> VertexAiRagRetrieval:
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