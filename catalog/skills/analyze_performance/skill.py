"""
Skill: Analyze Performance
Analisa métricas de performance do agente com histórico e recomendações.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Preços por 1M tokens (USD) - Vertex AI
PRICING = {
    "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-2.5-flash-lite": {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-3-flash-preview": {"input": 0.15, "output": 0.60},
}

# Thresholds para alertas
THRESHOLDS = {
    "latency_warning_ms": 10000,
    "latency_critical_ms": 30000,
    "cost_warning_usd": 0.05,
    "cost_critical_usd": 0.10,
    "translation_overhead_pct": 20,
}


@dataclass
class ModelMetrics:
    """Métricas agregadas por modelo."""
    model_name: str
    call_count: int = 0
    total_prompt_tokens: int = 0
    total_response_tokens: int = 0
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    cost_usd: float = 0.0


@dataclass
class SessionMetrics:
    """Métricas agregadas da sessão."""
    session_id: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_duration_ms: float = 0.0
    total_calls: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    models: Dict[str, ModelMetrics] = field(default_factory=dict)
    tool_calls: List[str] = field(default_factory=list)
    interaction_types: Dict[str, int] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Relatório completo de performance."""
    session_metrics: SessionMetrics
    latency_breakdown: List[Dict]
    token_distribution: List[Dict]
    alerts: List[Dict]
    recommendations: List[str]
    comparison: Optional[Dict] = None


def calculate_cost(model: str, prompt_tokens: int, response_tokens: int) -> float:
    """Calcula custo em USD baseado no modelo e tokens."""
    if model not in PRICING:
        # Fallback para modelo desconhecido
        logger.warning(f"Modelo {model} não encontrado na tabela de preços, usando flash como fallback")
        model = "gemini-2.5-flash"

    pricing = PRICING[model]
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (response_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def extract_metrics_from_state(state: Dict[str, Any]) -> SessionMetrics:
    """Extrai métricas do state da sessão."""
    session_id = state.get("session_id", "unknown")
    metrics = SessionMetrics(session_id=session_id)

    # Extrair usage stats por modelo
    usage_stats = state.get("model_usage_stats", {})
    for model_name, stats in usage_stats.items():
        model_metrics = ModelMetrics(model_name=model_name)
        model_metrics.total_prompt_tokens = stats.get("prompt", 0)
        model_metrics.total_response_tokens = stats.get("candidates", 0)
        model_metrics.total_tokens = stats.get("total", 0)
        model_metrics.cost_usd = calculate_cost(
            model_name,
            model_metrics.total_prompt_tokens,
            model_metrics.total_response_tokens
        )
        metrics.models[model_name] = model_metrics
        metrics.total_tokens += model_metrics.total_tokens
        metrics.total_cost_usd += model_metrics.cost_usd

    return metrics


def extract_metrics_from_reports(reports: List[Dict]) -> SessionMetrics:
    """Extrai métricas de uma lista de FinOps reports."""
    if not reports:
        return SessionMetrics(session_id="unknown")

    session_id = reports[0].get("session_id", "unknown") if reports else "unknown"
    metrics = SessionMetrics(session_id=session_id)

    timestamps = []

    for report in reports:
        model = report.get("model_name", "unknown")
        interaction_kind = report.get("interaction_kind", "agent")

        # Inicializar modelo se não existir
        if model not in metrics.models:
            metrics.models[model] = ModelMetrics(model_name=model)

        model_metrics = metrics.models[model]
        model_metrics.call_count += 1
        model_metrics.total_prompt_tokens += report.get("prompt_token_count", 0)
        model_metrics.total_response_tokens += report.get("candidates_token_count", 0)
        model_metrics.total_tokens += report.get("total_token_count", 0)
        model_metrics.total_latency_ms += report.get("execution_time_ms", 0)

        # Tipo de interação
        metrics.interaction_types[interaction_kind] = metrics.interaction_types.get(interaction_kind, 0) + 1

        # Timestamps
        ts = report.get("interaction_timestamp")
        if ts:
            timestamps.append(ts)

        metrics.total_calls += 1

    # Calcular médias e custos
    for model_name, model_metrics in metrics.models.items():
        if model_metrics.call_count > 0:
            model_metrics.avg_latency_ms = model_metrics.total_latency_ms / model_metrics.call_count
        model_metrics.cost_usd = calculate_cost(
            model_name,
            model_metrics.total_prompt_tokens,
            model_metrics.total_response_tokens
        )
        metrics.total_tokens += model_metrics.total_tokens
        metrics.total_cost_usd += model_metrics.cost_usd
        metrics.total_duration_ms += model_metrics.total_latency_ms

    # Timestamps da sessão
    if timestamps:
        metrics.start_time = min(timestamps)
        metrics.end_time = max(timestamps)

    return metrics


def generate_latency_breakdown(metrics: SessionMetrics) -> List[Dict]:
    """Gera breakdown de latência por modelo."""
    breakdown = []
    total_latency = metrics.total_duration_ms or 1  # Evitar divisão por zero

    for model_name, model_metrics in metrics.models.items():
        pct = (model_metrics.total_latency_ms / total_latency) * 100 if total_latency > 0 else 0
        breakdown.append({
            "model": model_name,
            "calls": model_metrics.call_count,
            "total_ms": round(model_metrics.total_latency_ms, 2),
            "avg_ms": round(model_metrics.avg_latency_ms, 2),
            "percentage": round(pct, 1),
        })

    # Ordenar por latência total
    breakdown.sort(key=lambda x: x["total_ms"], reverse=True)
    return breakdown


def generate_token_distribution(metrics: SessionMetrics) -> List[Dict]:
    """Gera distribuição de tokens por modelo."""
    distribution = []

    for model_name, model_metrics in metrics.models.items():
        distribution.append({
            "model": model_name,
            "prompt_tokens": model_metrics.total_prompt_tokens,
            "response_tokens": model_metrics.total_response_tokens,
            "total_tokens": model_metrics.total_tokens,
            "cost_usd": round(model_metrics.cost_usd, 6),
        })

    # Ordenar por tokens total
    distribution.sort(key=lambda x: x["total_tokens"], reverse=True)
    return distribution


def generate_alerts(metrics: SessionMetrics, latency_breakdown: List[Dict]) -> List[Dict]:
    """Gera alertas baseados nos thresholds."""
    alerts = []

    # Alerta de latência
    for item in latency_breakdown:
        if item["avg_ms"] > THRESHOLDS["latency_critical_ms"]:
            alerts.append({
                "level": "critical",
                "type": "latency",
                "message": f"Latência crítica no modelo {item['model']}: {item['avg_ms']:.0f}ms (limite: {THRESHOLDS['latency_critical_ms']}ms)",
            })
        elif item["avg_ms"] > THRESHOLDS["latency_warning_ms"]:
            alerts.append({
                "level": "warning",
                "type": "latency",
                "message": f"Latência alta no modelo {item['model']}: {item['avg_ms']:.0f}ms (limite: {THRESHOLDS['latency_warning_ms']}ms)",
            })

    # Alerta de custo
    if metrics.total_cost_usd > THRESHOLDS["cost_critical_usd"]:
        alerts.append({
            "level": "critical",
            "type": "cost",
            "message": f"Custo crítico da sessão: ${metrics.total_cost_usd:.4f} (limite: ${THRESHOLDS['cost_critical_usd']})",
        })
    elif metrics.total_cost_usd > THRESHOLDS["cost_warning_usd"]:
        alerts.append({
            "level": "warning",
            "type": "cost",
            "message": f"Custo alto da sessão: ${metrics.total_cost_usd:.4f} (limite: ${THRESHOLDS['cost_warning_usd']})",
        })

    # Alerta de overhead de tradução
    translation_count = metrics.interaction_types.get("translation", 0)
    if translation_count > 0 and metrics.total_calls > 0:
        translation_pct = (translation_count / metrics.total_calls) * 100

        # Calcular overhead de latência da tradução
        translation_model = None
        for model in metrics.models:
            if "lite" in model or "2.0-flash" in model:
                translation_model = model
                break

        if translation_model and metrics.total_duration_ms > 0:
            translation_latency = metrics.models[translation_model].total_latency_ms
            overhead_pct = (translation_latency / metrics.total_duration_ms) * 100

            if overhead_pct > THRESHOLDS["translation_overhead_pct"]:
                alerts.append({
                    "level": "warning",
                    "type": "translation_overhead",
                    "message": f"Overhead de tradução alto: {overhead_pct:.1f}% do tempo total (limite: {THRESHOLDS['translation_overhead_pct']}%)",
                })

    return alerts


def generate_recommendations(metrics: SessionMetrics, alerts: List[Dict], latency_breakdown: List[Dict]) -> List[str]:
    """Gera recomendações baseadas na análise."""
    recommendations = []

    # Recomendações baseadas em alertas
    for alert in alerts:
        if alert["type"] == "latency" and alert["level"] == "critical":
            recommendations.append(
                "Considere usar um modelo mais leve (flash-lite) para reduzir latência"
            )
        if alert["type"] == "cost" and alert["level"] in ["warning", "critical"]:
            recommendations.append(
                "Revise o uso de modelos Pro - considere Flash para tarefas simples"
            )
        if alert["type"] == "translation_overhead":
            recommendations.append(
                "Avalie se tradução é necessária para todas as interações"
            )

    # Recomendações baseadas em padrões
    if metrics.total_calls > 5:
        recommendations.append(
            "Sessão com muitas chamadas - considere consolidar prompts"
        )

    # Análise de modelos
    pro_usage = sum(1 for m in metrics.models if "pro" in m.lower())
    if pro_usage > 0 and metrics.total_cost_usd > 0.02:
        recommendations.append(
            "Modelo Pro está sendo usado - verifique se a qualidade extra justifica o custo"
        )

    # Recomendação baseada em alertas sem ação específica
    if alerts and not recommendations:
        recommendations.append(
            "Revisar os alertas acima e avaliar ações corretivas"
        )

    # Recomendação positiva se tudo estiver bem
    if not alerts and not recommendations:
        recommendations.append(
            "Performance dentro dos parâmetros esperados - nenhuma ação necessária"
        )

    return list(set(recommendations))  # Remove duplicatas


def format_duration(ms: float) -> str:
    """Formata duração em formato legível."""
    if ms < 1000:
        return f"{ms:.0f}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    return f"{minutes:.1f}min"


def generate_markdown_report(report: PerformanceReport) -> str:
    """Gera relatório em formato Markdown."""
    metrics = report.session_metrics

    md = []
    md.append("# 📊 Relatório de Performance do Agente\n")

    # Timestamp
    md.append(f"*Gerado em: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC*\n")

    # Resumo
    md.append("## Resumo da Sessão\n")
    md.append("| Métrica | Valor |")
    md.append("|---------|-------|")
    md.append(f"| Session ID | `{metrics.session_id[:8]}...` |")
    md.append(f"| Duração total | {format_duration(metrics.total_duration_ms)} |")
    md.append(f"| Chamadas ao modelo | {metrics.total_calls} |")
    md.append(f"| Tokens consumidos | {metrics.total_tokens:,} |")
    md.append(f"| Custo estimado | ${metrics.total_cost_usd:.4f} |")
    md.append("")

    # Alertas
    if report.alerts:
        md.append("## ⚠️ Alertas\n")
        for alert in report.alerts:
            icon = "🔴" if alert["level"] == "critical" else "🟡"
            md.append(f"- {icon} **{alert['level'].upper()}**: {alert['message']}")
        md.append("")

    # Latência
    md.append("## ⏱️ Latência por Modelo\n")
    md.append("| Modelo | Chamadas | Total | Média | % do Total |")
    md.append("|--------|----------|-------|-------|------------|")
    for item in report.latency_breakdown:
        md.append(f"| {item['model']} | {item['calls']} | {format_duration(item['total_ms'])} | {format_duration(item['avg_ms'])} | {item['percentage']}% |")
    md.append("")

    # Tokens
    md.append("## 🎫 Distribuição de Tokens\n")
    md.append("| Modelo | Input | Output | Total | Custo |")
    md.append("|--------|-------|--------|-------|-------|")
    for item in report.token_distribution:
        md.append(f"| {item['model']} | {item['prompt_tokens']:,} | {item['response_tokens']:,} | {item['total_tokens']:,} | ${item['cost_usd']:.4f} |")
    md.append("")

    # Tipos de interação
    if metrics.interaction_types:
        md.append("## 🔄 Tipos de Interação\n")
        md.append("| Tipo | Quantidade |")
        md.append("|------|------------|")
        for itype, count in metrics.interaction_types.items():
            md.append(f"| {itype} | {count} |")
        md.append("")

    # Comparação histórica
    if report.comparison:
        md.append("## 📈 Comparação com Média Histórica\n")
        md.append("| Métrica | Esta Sessão | Média | Variação |")
        md.append("|---------|-------------|-------|----------|")
        for metric_name, values in report.comparison.items():
            current = values.get("current", 0)
            avg = values.get("average", 0)
            if avg > 0:
                variation = ((current - avg) / avg) * 100
                arrow = "📈" if variation > 0 else "📉"
                md.append(f"| {metric_name} | {current:.2f} | {avg:.2f} | {arrow} {variation:+.1f}% |")
        md.append("")

    # Recomendações
    md.append("## 💡 Recomendações\n")
    for i, rec in enumerate(report.recommendations, 1):
        md.append(f"{i}. {rec}")
    md.append("")

    # Tabela de preços
    md.append("---\n")
    md.append("*Preços baseados na tabela Vertex AI (por 1M tokens)*")

    return "\n".join(md)


def analyze_performance(
    state: Optional[Dict[str, Any]] = None,
    reports: Optional[List[Dict]] = None,
    historical_data: Optional[List[SessionMetrics]] = None,
) -> PerformanceReport:
    """
    Analisa performance do agente e gera relatório completo.

    Args:
        state: State da sessão atual (opcional)
        reports: Lista de FinOps reports (opcional)
        historical_data: Dados históricos para comparação (opcional)

    Returns:
        PerformanceReport com análise completa
    """
    # Extrair métricas
    if reports:
        metrics = extract_metrics_from_reports(reports)
    elif state:
        metrics = extract_metrics_from_state(state)
    else:
        metrics = SessionMetrics(session_id="empty")

    # Gerar análises
    latency_breakdown = generate_latency_breakdown(metrics)
    token_distribution = generate_token_distribution(metrics)
    alerts = generate_alerts(metrics, latency_breakdown)
    recommendations = generate_recommendations(metrics, alerts, latency_breakdown)

    # Comparação histórica
    comparison = None
    if historical_data and len(historical_data) > 0:
        avg_duration = sum(h.total_duration_ms for h in historical_data) / len(historical_data)
        avg_tokens = sum(h.total_tokens for h in historical_data) / len(historical_data)
        avg_cost = sum(h.total_cost_usd for h in historical_data) / len(historical_data)
        avg_calls = sum(h.total_calls for h in historical_data) / len(historical_data)

        comparison = {
            "Duração (ms)": {"current": metrics.total_duration_ms, "average": avg_duration},
            "Tokens": {"current": metrics.total_tokens, "average": avg_tokens},
            "Custo ($)": {"current": metrics.total_cost_usd, "average": avg_cost},
            "Chamadas": {"current": metrics.total_calls, "average": avg_calls},
        }

    return PerformanceReport(
        session_metrics=metrics,
        latency_breakdown=latency_breakdown,
        token_distribution=token_distribution,
        alerts=alerts,
        recommendations=recommendations,
        comparison=comparison,
    )


# Função de conveniência para gerar relatório em Markdown
def get_performance_report_md(
    state: Optional[Dict[str, Any]] = None,
    reports: Optional[List[Dict]] = None,
) -> str:
    """Gera relatório de performance em formato Markdown."""
    report = analyze_performance(state=state, reports=reports)
    return generate_markdown_report(report)
