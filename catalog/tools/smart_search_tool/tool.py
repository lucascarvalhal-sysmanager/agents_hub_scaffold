"""
Tool: Smart Search Tool
Combina o SearchAgent com a skill smart_search para resultados estruturados.
"""

import logging
from typing import Any
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

logger = logging.getLogger(__name__)

# Sub-agente que faz a busca e já formata os resultados
smart_search_agent = Agent(
    model='gemini-2.5-flash',
    name='SmartSearchAgent',
    instruction="""Você é um especialista em pesquisas estruturadas.

Quando receber uma query de pesquisa:

1. Use a ferramenta google_search para buscar
2. Analise os resultados obtidos
3. Retorne um relatório estruturado no formato:

## 🔍 Pesquisa: [query]

### Resumo
[Resumo em 2-3 linhas dos principais achados]

### 📌 Pontos-Chave
- [Ponto 1]
- [Ponto 2]
- [Ponto 3]

### 📊 Categorias encontradas
- Notícias: X resultados
- Documentação: X resultados
- Tutoriais: X resultados
- Outros: X resultados

### 📚 Fontes
1. **[Título]** - [URL]
   - Relevância: Alta/Média/Baixa
   - Resumo: [snippet]

2. **[Título]** - [URL]
   - Relevância: Alta/Média/Baixa
   - Resumo: [snippet]

[Continue para todas as fontes]

### 💡 Recomendação
[Qual fonte é mais relevante para a query e por quê]

IMPORTANTE:
- Sempre categorize os resultados (notícia, documentação, tutorial, fórum, vídeo, oficial)
- Avalie a relevância de cada resultado para a query
- Destaque os pontos mais importantes
- Responda em português
""",
    tools=[google_search],
)

# Exporta como AgentTool para uso no agente principal
smart_search_tool = AgentTool(smart_search_agent)
