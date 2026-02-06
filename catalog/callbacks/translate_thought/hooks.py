import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
import google.genai as genai

logger = logging.getLogger(__name__)

# Configurações
TRANSLATION_MODEL = "gemini-2.5-flash-lite"
MIN_TEXT_LENGTH = 10

def _translate_to_ptbr(text: str) -> Tuple[str, Optional[types.GenerateContentResponseUsageMetadata], float]:
    """Traduz texto do inglês para português usando Gemini."""
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return text, None, 0.0

    try:
        logger.info(f"Iniciando tradução ({len(text)} chars)")
        client = genai.Client(vertexai=True)

        start_time = time.time()
        response = client.models.generate_content(
            model=TRANSLATION_MODEL,
            contents=f"Traduza o seguinte texto para português do Brasil. Retorne APENAS a tradução, sem explicações:\n\n{text}"
        )
        duration_ms = (time.time() - start_time) * 1000.0

        logger.info("Tradução concluída")
        return response.text.strip(), response.usage_metadata, duration_ms
    except Exception as e:
        logger.error(f"Erro ao traduzir: {e}")
        return text, None, 0.0


def _create_finops_report(
    original_text: str,
    translated_text: str,
    usage_meta: Any,
    duration_ms: float
) -> Optional[Dict]:
    """Cria relatório FinOps para a tradução."""
    try:
        from agents.helpers.finops_persistence import FinopsReport

        p_count = getattr(usage_meta, "prompt_token_count", 0)
        c_count = getattr(usage_meta, "candidates_token_count", 0)
        t_count = getattr(usage_meta, "total_token_count", 0)

        return FinopsReport(
            user_prompt=original_text,
            agent_response=translated_text,
            model_name=TRANSLATION_MODEL,
            prompt_token_count=p_count,
            candidates_token_count=c_count,
            total_token_count=t_count,
            execution_time_ms=duration_ms,
            interaction_timestamp=datetime.now(timezone.utc).isoformat(),
            interaction_kind="translation"
        )
    except ImportError:
        logger.debug("FinOps não disponível, pulando relatório")
        return None


def translate_thought(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Intercepta o pensamento REAL do Gemini e traduz para português.

    Uso: Registrar como after_model_callback no agente.
    """
    if not llm_response.content or not llm_response.content.parts:
        return llm_response

    new_parts = []
    modified = False

    for part in llm_response.content.parts:
        if hasattr(part, 'thought') and part.thought and part.text:
            translated_text, usage_meta, duration_ms = _translate_to_ptbr(part.text)

            if usage_meta:
                try:
                    # 1. Update Global Usage Stats
                    state_data = callback_context.state.to_dict()
                    usage_stats = state_data.get("model_usage_stats", {})

                    if TRANSLATION_MODEL not in usage_stats:
                        usage_stats[TRANSLATION_MODEL] = {"prompt": 0, "candidates": 0, "total": 0}

                    p_count = getattr(usage_meta, "prompt_token_count", 0)
                    c_count = getattr(usage_meta, "candidates_token_count", 0)
                    t_count = getattr(usage_meta, "total_token_count", 0)

                    usage_stats[TRANSLATION_MODEL]["prompt"] += p_count
                    usage_stats[TRANSLATION_MODEL]["candidates"] += c_count
                    usage_stats[TRANSLATION_MODEL]["total"] += t_count

                    callback_context.state["model_usage_stats"] = usage_stats
                    logger.info(f"Tradução para pt-br contabilizada: +{t_count} tokens ({TRANSLATION_MODEL})")

                    # 2. Create FinOps Report
                    report = _create_finops_report(part.text, translated_text, usage_meta, duration_ms)
                    if report:
                        side_reports = state_data.get("temp:finops_side_reports", [])
                        side_reports.append(report)
                        callback_context.state["temp:finops_side_reports"] = side_reports

                except Exception as e:
                    logger.warning(f"Falha ao registrar uso de tradução no state: {e}")

            new_parts.append(types.Part(thought=True, text=translated_text))
            modified = True
        else:
            new_parts.append(part)

    if modified:
        if hasattr(llm_response, 'content'):
            llm_response.content.parts = new_parts
        return None

    return None
