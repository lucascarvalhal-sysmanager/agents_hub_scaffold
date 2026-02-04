"""
Skill: Smart Search
Pesquisa inteligente com resultados estruturados, fontes e análise.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ResultCategory(Enum):
    """Categorias de resultados de pesquisa."""
    NEWS = "notícias"
    ARTICLE = "artigo"
    DOCUMENTATION = "documentação"
    TUTORIAL = "tutorial"
    FORUM = "fórum"
    VIDEO = "vídeo"
    OFFICIAL = "oficial"
    OTHER = "outro"


@dataclass
class SearchSource:
    """Fonte de um resultado de pesquisa."""
    title: str
    url: str
    snippet: str
    category: ResultCategory = ResultCategory.OTHER
    relevance_score: float = 0.0


@dataclass
class SearchResult:
    """Resultado estruturado de uma pesquisa."""
    query: str
    timestamp: str
    summary: str
    key_points: List[str]
    sources: List[SearchSource]
    categories: Dict[str, int]
    total_results: int
    search_time_ms: float = 0.0


def _categorize_url(url: str, title: str) -> ResultCategory:
    """Categoriza um resultado baseado na URL e título."""
    url_lower = url.lower()
    title_lower = title.lower()

    # Documentação oficial
    if any(x in url_lower for x in ['docs.', 'documentation', 'developer.', 'api.']):
        return ResultCategory.DOCUMENTATION

    # Sites oficiais
    if any(x in url_lower for x in ['.gov', '.org', 'official']):
        return ResultCategory.OFFICIAL

    # Notícias
    if any(x in url_lower for x in ['news', 'noticias', 'blog', 'medium.com']):
        return ResultCategory.NEWS

    # Tutoriais
    if any(x in title_lower for x in ['tutorial', 'como fazer', 'how to', 'guia', 'guide']):
        return ResultCategory.TUTORIAL

    # Fóruns
    if any(x in url_lower for x in ['stackoverflow', 'reddit', 'forum', 'community']):
        return ResultCategory.FORUM

    # Vídeos
    if any(x in url_lower for x in ['youtube', 'vimeo', 'video']):
        return ResultCategory.VIDEO

    # Artigos
    if any(x in title_lower for x in ['artigo', 'article', 'análise', 'analysis']):
        return ResultCategory.ARTICLE

    return ResultCategory.OTHER


def _calculate_relevance(title: str, snippet: str, query: str) -> float:
    """Calcula score de relevância (0-1) baseado na query."""
    query_terms = query.lower().split()
    text = f"{title} {snippet}".lower()

    matches = sum(1 for term in query_terms if term in text)
    return matches / len(query_terms) if query_terms else 0.0


def _extract_key_points(sources: List[SearchSource], max_points: int = 5) -> List[str]:
    """Extrai pontos-chave dos snippets."""
    key_points = []

    # Ordenar por relevância
    sorted_sources = sorted(sources, key=lambda x: x.relevance_score, reverse=True)

    for source in sorted_sources[:max_points]:
        # Limpar e truncar snippet
        snippet = source.snippet.strip()
        if len(snippet) > 150:
            snippet = snippet[:147] + "..."
        if snippet and snippet not in key_points:
            key_points.append(snippet)

    return key_points


def _generate_summary(query: str, sources: List[SearchSource]) -> str:
    """Gera um resumo dos resultados."""
    if not sources:
        return f"Nenhum resultado encontrado para: {query}"

    categories = {}
    for source in sources:
        cat = source.category.value
        categories[cat] = categories.get(cat, 0) + 1

    cat_str = ", ".join([f"{count} {cat}" for cat, count in categories.items()])

    return f"Encontrados {len(sources)} resultados para \"{query}\": {cat_str}."


def _format_markdown_report(result: SearchResult) -> str:
    """Formata o resultado em Markdown."""
    md = []

    md.append(f"# 🔍 Pesquisa: {result.query}\n")
    md.append(f"*{result.timestamp}*\n")

    # Resumo
    md.append("## Resumo\n")
    md.append(f"{result.summary}\n")

    # Pontos-chave
    if result.key_points:
        md.append("## 📌 Pontos-Chave\n")
        for point in result.key_points:
            md.append(f"- {point}")
        md.append("")

    # Resultados por categoria
    if result.categories:
        md.append("## 📊 Por Categoria\n")
        md.append("| Categoria | Quantidade |")
        md.append("|-----------|------------|")
        for cat, count in sorted(result.categories.items(), key=lambda x: x[1], reverse=True):
            md.append(f"| {cat} | {count} |")
        md.append("")

    # Fontes
    md.append("## 📚 Fontes\n")
    for i, source in enumerate(result.sources, 1):
        relevance_bar = "🟢" if source.relevance_score > 0.7 else "🟡" if source.relevance_score > 0.4 else "🔴"
        md.append(f"### {i}. {source.title}")
        md.append(f"- **URL:** [{source.url}]({source.url})")
        md.append(f"- **Categoria:** {source.category.value}")
        md.append(f"- **Relevância:** {relevance_bar} {source.relevance_score:.0%}")
        md.append(f"- **Snippet:** {source.snippet}")
        md.append("")

    return "\n".join(md)


def process_search_results(
    query: str,
    raw_results: List[Dict[str, Any]],
    search_time_ms: float = 0.0
) -> SearchResult:
    """
    Processa resultados brutos de busca e retorna estruturado.

    Args:
        query: Query original da pesquisa
        raw_results: Lista de resultados brutos (title, url, snippet)
        search_time_ms: Tempo da pesquisa em ms

    Returns:
        SearchResult estruturado
    """
    sources = []
    categories = {}

    for item in raw_results:
        title = item.get("title", "Sem título")
        url = item.get("url", item.get("link", ""))
        snippet = item.get("snippet", item.get("description", ""))

        # Categorizar
        category = _categorize_url(url, title)
        categories[category.value] = categories.get(category.value, 0) + 1

        # Calcular relevância
        relevance = _calculate_relevance(title, snippet, query)

        source = SearchSource(
            title=title,
            url=url,
            snippet=snippet,
            category=category,
            relevance_score=relevance
        )
        sources.append(source)

    # Ordenar por relevância
    sources.sort(key=lambda x: x.relevance_score, reverse=True)

    # Extrair pontos-chave
    key_points = _extract_key_points(sources)

    # Gerar resumo
    summary = _generate_summary(query, sources)

    return SearchResult(
        query=query,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        summary=summary,
        key_points=key_points,
        sources=sources,
        categories=categories,
        total_results=len(sources),
        search_time_ms=search_time_ms
    )


def smart_search(
    query: str,
    raw_results: Optional[List[Dict[str, Any]]] = None,
    search_time_ms: float = 0.0,
    output_format: str = "markdown"
) -> str:
    """
    Executa pesquisa inteligente e retorna resultado formatado.

    Esta skill processa resultados de busca (da tool google_search)
    e retorna um relatório estruturado com:
    - Resumo dos resultados
    - Pontos-chave extraídos
    - Categorização das fontes
    - Lista de fontes com relevância

    Args:
        query: Termo de pesquisa
        raw_results: Resultados brutos (se None, retorna template)
        search_time_ms: Tempo da pesquisa
        output_format: Formato de saída (markdown, json, text)

    Returns:
        Resultado formatado
    """
    if raw_results is None:
        # Retornar instruções de uso
        return """
## Skill: Smart Search

Esta skill processa resultados de pesquisa do Google.

### Como usar:

1. Execute a tool `google_search` com sua query
2. Passe os resultados para `smart_search(query, raw_results)`
3. Receba o relatório estruturado

### Exemplo:
```python
from catalog.skills.smart_search import smart_search

# Após obter resultados da tool google_search
report = smart_search(
    query="inteligência artificial 2024",
    raw_results=search_results
)
print(report)
```
"""

    # Processar resultados
    result = process_search_results(query, raw_results, search_time_ms)

    # Formatar saída
    if output_format == "markdown":
        return _format_markdown_report(result)
    elif output_format == "json":
        import json
        return json.dumps({
            "query": result.query,
            "timestamp": result.timestamp,
            "summary": result.summary,
            "key_points": result.key_points,
            "categories": result.categories,
            "total_results": result.total_results,
            "sources": [
                {
                    "title": s.title,
                    "url": s.url,
                    "snippet": s.snippet,
                    "category": s.category.value,
                    "relevance": s.relevance_score
                }
                for s in result.sources
            ]
        }, indent=2, ensure_ascii=False)
    else:
        # Texto simples
        lines = [f"Pesquisa: {result.query}", f"Resultados: {result.total_results}", ""]
        lines.append("Pontos-chave:")
        for point in result.key_points:
            lines.append(f"  - {point}")
        lines.append("")
        lines.append("Fontes:")
        for s in result.sources:
            lines.append(f"  - {s.title}: {s.url}")
        return "\n".join(lines)


# Função auxiliar para integração com o agente
def get_search_report(query: str, raw_results: List[Dict], search_time_ms: float = 0.0) -> str:
    """Alias para smart_search com formato markdown."""
    return smart_search(query, raw_results, search_time_ms, "markdown")
