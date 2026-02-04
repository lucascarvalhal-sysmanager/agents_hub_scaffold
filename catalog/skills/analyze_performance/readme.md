# Skill: Analyze Performance

Analisa a performance do agente com métricas detalhadas, alertas e recomendações.

## Funcionalidades

- **Métricas por modelo**: Tokens, latência, custo
- **Métricas da sessão**: Duração, chamadas, custo total
- **Alertas automáticos**: Baseados em thresholds configuráveis
- **Recomendações**: Sugestões de otimização
- **Comparação histórica**: Evolução ao longo do tempo

## Uso

### Via Trigger (conversa)
```
Usuário: /analyze-performance
Usuário: como está a performance?
```

### Via Código
```python
from catalog.skills.analyze_performance import (
    analyze_performance,
    get_performance_report_md
)

# Gerar relatório a partir do state
report_md = get_performance_report_md(state=session_state)
print(report_md)

# Ou análise programática
report = analyze_performance(reports=finops_reports)
print(f"Custo total: ${report.session_metrics.total_cost_usd:.4f}")
```

## Métricas Coletadas

| Métrica | Fonte | Descrição |
|---------|-------|-----------|
| Tokens | FinOps | Input, output, total por modelo |
| Latência | FinOps | Tempo de execução por chamada |
| Custo | Calculado | Baseado na tabela Vertex AI |
| Tipo de interação | FinOps | agent, translation, tool |

## Thresholds

| Alerta | Warning | Critical |
|--------|---------|----------|
| Latência média | > 10s | > 30s |
| Custo da sessão | > $0.05 | > $0.10 |
| Overhead tradução | > 20% | - |

## Exemplo de Relatório

```markdown
# 📊 Relatório de Performance do Agente

## Resumo da Sessão
| Métrica | Valor |
|---------|-------|
| Duração total | 33.8s |
| Chamadas ao modelo | 4 |
| Tokens consumidos | 2,847 |
| Custo estimado | $0.0142 |

## ⏱️ Latência por Modelo
| Modelo | Chamadas | Total | Média | % do Total |
|--------|----------|-------|-------|------------|
| gemini-2.5-pro | 2 | 18.5s | 9.2s | 55% |
| gemini-2.5-flash | 1 | 11.2s | 11.2s | 33% |
| gemini-2.5-flash-lite | 1 | 4.0s | 4.0s | 12% |

## 💡 Recomendações
1. Performance dentro dos parâmetros esperados
```

## Configuração

Edite `spec.yaml` para ajustar:

```yaml
config:
  pricing:
    gemini-2.5-pro:
      input: 1.25
      output: 5.00
  thresholds:
    latency_warning_ms: 10000
    cost_warning_usd: 0.05
```

## Integração com FinOps

Esta skill utiliza os dados coletados pelos callbacks FinOps:

1. `finops_before_model` - Captura timestamp
2. `finops_after_model` - Coleta métricas
3. `finops_after_agent` - Persiste reports

## Autor

Eneva Foundations IA
