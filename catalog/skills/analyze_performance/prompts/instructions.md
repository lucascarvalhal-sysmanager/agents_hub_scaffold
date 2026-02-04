# Skill: Analyze Performance

## Descrição
Analisa a performance do agente na sessão atual, gerando um relatório completo com métricas, alertas e recomendações.

## Triggers
- `/analyze-performance`
- `/performance`
- "analise a performance"
- "como está a performance"

## Execução

### Passo 1: Coletar Dados
Extrair dados de performance das seguintes fontes:

1. **State da sessão** (`callback_context.state`):
   - `model_usage_stats`: Tokens por modelo
   - `temp:finops_reports`: Reports da sessão

2. **FinOps Reports** (se disponíveis):
   - `prompt_token_count`
   - `candidates_token_count`
   - `execution_time_ms`
   - `model_name`
   - `interaction_kind`

### Passo 2: Calcular Métricas

#### Por Modelo:
- Total de chamadas
- Tokens (input, output, total)
- Latência (total, média)
- Custo estimado (USD)

#### Por Sessão:
- Duração total
- Total de chamadas
- Total de tokens
- Custo total

### Passo 3: Gerar Alertas

Verificar thresholds:

| Métrica | Warning | Critical |
|---------|---------|----------|
| Latência média | > 10s | > 30s |
| Custo da sessão | > $0.05 | > $0.10 |
| Overhead de tradução | > 20% | - |

### Passo 4: Gerar Recomendações

Baseadas em:
- Alertas detectados
- Padrões de uso
- Comparação histórica (se disponível)

### Passo 5: Formatar Relatório

Gerar relatório em Markdown com:
- Resumo executivo
- Alertas (se houver)
- Breakdown de latência
- Distribuição de tokens
- Tipos de interação
- Comparação histórica (se disponível)
- Recomendações

## Exemplo de Output

```markdown
# 📊 Relatório de Performance do Agente

## Resumo da Sessão
| Métrica | Valor |
|---------|-------|
| Duração total | 33.8s |
| Chamadas ao modelo | 4 |
| Tokens consumidos | 2,847 |
| Custo estimado | $0.0142 |

## ⚠️ Alertas
- 🟡 **WARNING**: Latência alta no modelo gemini-2.5-pro: 9490ms

## 💡 Recomendações
1. Performance dentro dos parâmetros esperados
```

## Integração

### Como Tool (chamada manual):
```python
from catalog.skills.analyze_performance import get_performance_report_md

report = get_performance_report_md(state=callback_context.state.to_dict())
print(report)
```

### Como Callback (automático ao final):
```python
from catalog.skills.analyze_performance import analyze_performance

def after_agent_callback(callback_context):
    reports = callback_context.state.get("temp:finops_reports", [])
    report = analyze_performance(reports=reports)
    # Salvar ou exibir relatório
```

## Tabela de Preços (Vertex AI)

| Modelo | Input (1M) | Output (1M) |
|--------|------------|-------------|
| gemini-2.5-pro | $1.25 | $5.00 |
| gemini-2.5-flash | $0.15 | $0.60 |
| gemini-2.5-flash-lite | $0.075 | $0.30 |
| gemini-2.0-flash | $0.10 | $0.40 |
| gemini-3-flash-preview | $0.15 | $0.60 |
