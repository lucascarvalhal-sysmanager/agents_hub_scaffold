"""
Hooks - Re-exporta callbacks do catálogo para manter compatibilidade.

Os callbacks reais estão em: catalog/callbacks/translate_thought/
"""

from catalog.callbacks.translate_thought import translate_thought, inject_log_before_tool_callback

__all__ = ["translate_thought", "inject_log_before_tool_callback"]
