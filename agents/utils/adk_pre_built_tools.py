"""
ADK Pre-Built Tools - Re-exporta do catálogo para manter compatibilidade.

Os códigos reais estão em:
- catalog/tools/google_search/
- catalog/tools/vertex_rag/
- catalog/tools/smart_search_tool/
"""

from catalog.tools.google_search import search_agent, search_agent_tool
from catalog.tools.vertex_rag import build_vertex_rag_tool
from catalog.tools.smart_search_tool import smart_search_tool, smart_search_agent

__all__ = [
    "search_agent",
    "search_agent_tool",
    "build_vertex_rag_tool",
    "smart_search_tool",
    "smart_search_agent",
]
