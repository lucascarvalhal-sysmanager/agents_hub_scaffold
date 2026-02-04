"""
Skill: Smart Search
Pesquisa inteligente com resultados estruturados.
"""

from .skill import (
    smart_search,
    get_search_report,
    process_search_results,
    SearchResult,
    SearchSource,
    ResultCategory,
)

__all__ = [
    "smart_search",
    "get_search_report",
    "process_search_results",
    "SearchResult",
    "SearchSource",
    "ResultCategory",
]
