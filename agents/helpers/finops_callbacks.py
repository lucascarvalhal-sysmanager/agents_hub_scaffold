"""
FinOps Callbacks - Re-exporta do catálogo para manter compatibilidade.

Os códigos reais estão em:
- catalog/callbacks/finops_before_model/
- catalog/callbacks/finops_after_model/
- catalog/callbacks/finops_after_agent/
"""

from catalog.callbacks.finops_before_model import finops_before_model_callback
from catalog.callbacks.finops_after_model import collect_finops_metrics
from catalog.callbacks.finops_after_agent import persist_finops_metrics, get_finops_service

__all__ = [
    "finops_before_model_callback",
    "collect_finops_metrics",
    "persist_finops_metrics",
    "get_finops_service"
]
