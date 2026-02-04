"""
FinOps Persistence - Re-exporta do catálogo para manter compatibilidade.

Os códigos reais estão em: catalog/callbacks/finops_persistence/
"""

from catalog.callbacks.finops_persistence import (
    FinopsReport,
    PersistenceProvider,
    BigQueryProvider,
    FinopsPersistenceService,
    PersistenceFactory
)

__all__ = [
    "FinopsReport",
    "PersistenceProvider",
    "BigQueryProvider",
    "FinopsPersistenceService",
    "PersistenceFactory"
]
