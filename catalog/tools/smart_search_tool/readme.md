# Tool: Smart Search Tool

Pesquisa inteligente que combina o `google_search` com formatação estruturada.

## Diferença do SearchAgent original

| Aspecto | SearchAgent | SmartSearchAgent |
|---------|-------------|------------------|
| **Output** | Texto livre | Relatório estruturado |
| **Categorização** | Não | Sim |
| **Relevância** | Não | Sim |
| **Pontos-chave** | Não | Sim |
| **Recomendação** | Não | Sim |

## Formato de saída

```markdown
## 🔍 Pesquisa: [query]

### Resumo
[2-3 linhas]

### 📌 Pontos-Chave
- Ponto 1
- Ponto 2

### 📊 Categorias
- Notícias: 2
- Documentação: 1

### 📚 Fontes
1. **Título** - URL
   - Relevância: Alta
   - Resumo: ...

### 💡 Recomendação
[Qual fonte é mais relevante]
```

## Uso

### No config.yaml
```yaml
agent:
  name: meu_agente
  tools:
    - SmartSearchAgent  # Ao invés de SearchAgent

tools:
  - name: SmartSearchAgent
    transport: pre_built
    type: smart_search_tool
```

### Via código
```python
from catalog.tools.smart_search_tool import smart_search_tool

# Usar como ferramenta do agente
agent = Agent(
    name="meu_agente",
    tools=[smart_search_tool],
    ...
)
```

## Autor

Eneva Foundations IA
