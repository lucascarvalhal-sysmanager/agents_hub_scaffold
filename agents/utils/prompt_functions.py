"""
Prompt Functions - Re-exporta do catálogo para manter compatibilidade.

Os códigos reais estão em: catalog/tools/datetime_tool/
"""

from catalog.tools.datetime_tool import get_current_datetime, formatted_date_today

__all__ = ["get_current_datetime", "formatted_date_today"]
