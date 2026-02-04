# Skill: Smart Search

Pesquisa inteligente que transforma resultados brutos em relatórios estruturados.

## Diferença: Tool vs Skill

| Aspecto | Tool (google_search) | Skill (smart_search) |
|---------|---------------------|----------------------|
| **O que faz** | Executa busca no Google | Processa e formata resultados |
| **Input** | Query de texto | Resultados brutos + query |
| **Output** | Lista de links | Relatório estruturado |
| **Inteligência** | Nenhuma | Categoriza, ranqueia, resume |

## Funcionalidades

- **Categorização automática** - Identifica tipo de fonte (notícia, documentação, tutorial, etc.)
- **Score de relevância** - Calcula quão relevante cada resultado é para a query
- **Extração de pontos-chave** - Resume os principais insights
- **Múltiplos formatos** - Markdown, JSON ou texto simples

## Uso

### Via código
```python
from catalog.skills.smart_search import smart_search

# Resultados brutos (da tool google_search)
raw_results = [
    {"title": "IA em 2024", "url": "https://...", "snippet": "..."},
    {"title": "Tendências tech", "url": "https://...", "snippet": "..."},
]

# Processar com a skill
report = smart_search(
    query="inteligência artificial",
    raw_results=raw_results,
    output_format="markdown"
)

print(report)
```

### Formatos de saída

**Markdown** (padrão)
```markdown
# 🔍 Pesquisa: query
## Resumo
...
## Fontes
...
```

**JSON**
```json
{
  "query": "...",
  "summary": "...",
  "sources": [...]
}
```

**Texto**
```
Pesquisa: query
Resultados: 5
Pontos-chave:
  - ...
```

## Categorias suportadas

| Categoria | Detectado por |
|-----------|---------------|
| 📰 Notícias | news, blog, medium.com |
| 📚 Documentação | docs., documentation, api. |
| 🎓 Tutorial | tutorial, how to, guia |
| 💬 Fórum | stackoverflow, reddit, forum |
| 🎬 Vídeo | youtube, vimeo |
| 🏛️ Oficial | .gov, .org |
| 📄 Artigo | article, análise |

## Fluxo completo

```
Usuário: "Pesquise sobre IA em 2024"
    │
    ▼
┌─────────────────────────────────────┐
│ Agente detecta intenção de pesquisa │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Tool: google_search("IA 2024")      │
│ Output: [{title, url, snippet}, ...]│
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Skill: smart_search(query, results) │
│ - Categoriza                        │
│ - Calcula relevância                │
│ - Extrai pontos-chave               │
│ - Formata relatório                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Relatório estruturado para usuário  │
└─────────────────────────────────────┘
```

## Autor

Eneva Foundations IA
