# Skill: Smart Search

## Descrição
Transforma resultados brutos de pesquisa do Google em um relatório estruturado e categorizado.

## Triggers
- `/search <query>`
- `/pesquisar <query>`
- "pesquise sobre..."
- "busque informações sobre..."

## Fluxo de Execução

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Usuário pede   │ ──► │  Tool executa   │ ──► │  Skill processa │
│  pesquisa       │     │  google_search  │     │  smart_search   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Relatório      │
                                                │  estruturado    │
                                                └─────────────────┘
```

## O que a Skill faz

### 1. Categoriza resultados
- 📰 Notícias
- 📄 Artigos
- 📚 Documentação
- 🎓 Tutoriais
- 💬 Fóruns
- 🎬 Vídeos
- 🏛️ Oficial
- 📦 Outros

### 2. Calcula relevância
- Compara termos da query com título e snippet
- Score de 0% a 100%
- 🟢 Alta (>70%) | 🟡 Média (40-70%) | 🔴 Baixa (<40%)

### 3. Extrai pontos-chave
- Seleciona os snippets mais relevantes
- Remove duplicatas
- Limita a 5 pontos

### 4. Gera relatório
- Resumo executivo
- Pontos-chave
- Distribuição por categoria
- Lista de fontes com metadados

## Exemplo de Output

```markdown
# 🔍 Pesquisa: inteligência artificial 2024

## Resumo
Encontrados 5 resultados: 2 notícias, 2 artigos, 1 documentação.

## 📌 Pontos-Chave
- IA generativa domina mercado em 2024
- Regulamentação avança na Europa
- Novos modelos multimodais lançados

## 📊 Por Categoria
| Categoria | Quantidade |
|-----------|------------|
| notícias | 2 |
| artigo | 2 |
| documentação | 1 |

## 📚 Fontes
### 1. OpenAI lança GPT-5
- **URL:** https://...
- **Categoria:** notícias
- **Relevância:** 🟢 85%
```

## Integração

### No agente (automático)
O agente pode usar esta skill automaticamente quando detectar intenção de pesquisa.

### Via código
```python
from catalog.skills.smart_search import smart_search

# Após obter resultados da tool google_search
report = smart_search(
    query="tendências tecnologia 2024",
    raw_results=google_search_results,
    output_format="markdown"  # ou "json", "text"
)
```

## Configuração

```yaml
config:
  max_results: 5
  include_sources: true
  categorize_results: true
  generate_summary: true
  output_format: markdown
```
